from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.db.models import OuterRef, Exists, Sum, Subquery, Count, Max, Q
from django.template.loader import render_to_string

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import django.forms as forms
import django.urls as urls

from .models import Hunt, User, Team, Puzzle, Guess, ExtraGuessGrant


def index(request):
    # user = request.user
    hunts = Hunt.objects.all()
    return render(
        request,
        "index.html",
        {
            "hunts": hunts,
        },
    )


class MarkdownTextarea(forms.Textarea):
    template_name = "widgets/markdown_textarea.html"


# based on UserCreationForm from Django source
class RegisterForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        help_text="Enter the same password as above, for verification.",
    )
    email = forms.EmailField(
        label="Email address",
        required=False,
        help_text="Optional, but you'll get useful email notifications when we implement those.",
    )
    bio = forms.CharField(
        widget=MarkdownTextarea,
        required=False,
        help_text="(optional) Tell us about yourself. What kinds of puzzle genres or subject matter do you like?",
    )

    class Meta:
        model = User
        fields = ("username", "email", "display_name", "discord_username", "bio")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The two password fields didn't match.",
                code="password_mismatch",
            )
        return password2

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(urls.reverse("login"))
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = RegisterForm()
        return render(request, "register.html", {"form": form})


class HuntForm(forms.ModelForm):
    description = forms.CharField(widget=MarkdownTextarea, required=False)

    class Meta:
        model = Hunt
        fields = [
            "name",
            "description",
            "start_time",
            "end_time",
            "member_limit",
            "guess_limit",
        ]


@login_required
def new_hunt(request):
    if request.method == "POST":
        form = HuntForm(request.POST)
        if form.is_valid():
            hunt = form.save()

            # needs save before we can do many-to-many stuff
            hunt.organizers.add(request.user)

            return redirect(urls.reverse("view_hunt", args=[hunt.id]))
    else:
        form = HuntForm()

    return render(
        request,
        "new_hunt.html",
        {
            "form": form,
        },
    )


def get_team(user, hunt):
    if user.is_anonymous:
        return None

    try:
        return Team.objects.get(hunt=hunt, members=user)
    except Team.DoesNotExist:
        return None
    # bad if MultipleObjectsReturned


def view_hunt(request, id):
    user = request.user
    hunt = get_object_or_404(Hunt, id=id)
    team = get_team(user, hunt)
    is_organizer = user.is_authenticated and hunt.organizers.filter(id=user.id).exists()

    if is_organizer:
        puzzles = hunt.puzzles.all()
    elif team:
        puzzles = team.unlocked_puzzles_with_solved()
    else:
        puzzles = hunt.public_puzzles()

    puzzles = puzzles.annotate(
        solve_count=Count("guesses", filter=Q(guesses__correct=True)),
        guess_count=Count("guesses"),
    )

    return render(
        request,
        "view_hunt.html",
        {
            "hunt": hunt,
            "team": team,
            "puzzles": puzzles.order_by("order"),
            "is_organizer": is_organizer,
        },
    )


def leaderboard(request, id):
    user = request.user
    hunt = get_object_or_404(Hunt, id=id)
    team = get_team(user, hunt)
    is_organizer = user.is_authenticated and hunt.organizers.filter(id=user.id).exists()

    # for the sake of simplicity, assume teams won't end up with two correct guesses for a puzzle
    teams = hunt.teams.annotate(
        score=Subquery(
            Guess.objects.filter(
                team=OuterRef("pk"),
                correct=True,
            )
            .values("puzzle__points")
            .annotate(score=Sum("puzzle__points"))
            .values("score")
        ),
        solve_count=Count("guesses", filter=Q(guesses__correct=True)),
        last_solve=Subquery(
            Guess.objects.filter(
                team=OuterRef("pk"),
                correct=True,
            )
            .order_by("-time")[:1]
            .values("time")
        ),
    ).order_by("-score", "-solve_count", "last_solve")

    print(teams.query)

    return render(
        request,
        "leaderboard.html",
        {
            "hunt": hunt,
            "team": team,
            "teams": teams,
            "is_organizer": is_organizer,
        },
    )


class GuessForm(forms.Form):
    guess = forms.CharField()


def normalize_answer(answer):
    return "".join(c for c in answer if c.isalnum()).upper()


def view_puzzle(request, hunt_id, puzzle_id):
    user = request.user
    hunt = get_object_or_404(Hunt, id=hunt_id)
    puzzle = get_object_or_404(Puzzle, hunt=hunt, id=puzzle_id)
    team = get_team(user, hunt)

    is_organizer = user.is_authenticated and hunt.organizers.filter(id=user.id).exists()

    if not is_organizer and not puzzle.is_viewable_by(team):
        raise Http404("Puzzle is not viewable by team (or the public)")

    if team:
        solved = Guess.objects.filter(puzzle=puzzle, team=team, correct=True).exists()

        guess_limit = hunt.guess_limit
        guesses_limited = bool(guess_limit)

        if guesses_limited:
            try:
                grant = ExtraGuessGrant.objects.get(team=team, puzzle=puzzle)
                guess_limit += grant.extra_guesses
            except ExtraGuessGrant.DoesNotExist:
                pass

            guesses_remaining = (
                guess_limit - Guess.objects.filter(puzzle=puzzle, team=team).count()
            )
            guesses_at_limit = guesses_remaining <= 0
        else:
            # hunt doesn't limit guesses
            guesses_remaining = 0
            guesses_at_limit = False
    else:
        solved = False
        guesses_limited = None
        guesses_remaining = 0
        guesses_at_limit = False

    if request.method == "POST":
        guess_form = GuessForm(request.POST)

        if solved:
            error = "You have already solved the puzzle!"
        elif not guesses_at_limit and guess_form.is_valid():
            guess_text = normalize_answer(guess_form.cleaned_data["guess"])
            if Guess.objects.filter(
                guess=guess_text, team=team, puzzle=puzzle
            ).exists():
                guess_form.add_error("guess", "You have already guessed that answer!")
            else:
                guess = Guess(
                    guess=guess_text,
                    team=team,
                    user=user,
                    puzzle=puzzle,
                    correct=(guess_text == normalize_answer(puzzle.answer)),
                )
                guess.save()

                if guess.correct:
                    solved = True

                return redirect(urls.reverse("view_puzzle", args=[hunt_id, puzzle_id]))
    else:
        guess_form = GuessForm()

    return render(
        request,
        "view_puzzle.html",
        {
            "hunt": hunt,
            "team": team,
            "puzzle": puzzle,
            "solved": solved,
            "guesses_limited": guesses_limited,
            "guesses_remaining": guesses_remaining,
            "guesses_at_limit": guesses_at_limit,
            "guesses": Guess.objects.filter(team=team, puzzle=puzzle).order_by("time"),
            "guess_form": guess_form,
            "is_organizer": is_organizer,
        },
    )


def view_puzzle_log(request, hunt_id, puzzle_id):
    user = request.user
    hunt = get_object_or_404(Hunt, id=hunt_id)
    puzzle = get_object_or_404(Puzzle, hunt=hunt, id=puzzle_id)

    is_organizer = user.is_authenticated and hunt.organizers.filter(id=user.id).exists()

    if not is_organizer:
        raise Http404("Puzzle stats are only viewable by organizers")

    return render(
        request,
        "view_puzzle_log.html",
        {
            "hunt": hunt,
            "puzzle": puzzle,
            "guesses": Guess.objects.filter(puzzle=puzzle).order_by("time"),
        },
    )


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]


class InviteMemberForm(forms.Form):
    username = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("No such user!")

        cleaned_data["user"] = user
        return cleaned_data


@login_required
def my_team(request, id):
    user = request.user
    hunt = get_object_or_404(Hunt, id=id)
    team = get_team(user, hunt)
    error = None

    create_team_form = TeamForm()
    invite_member_form = InviteMemberForm()

    if request.method == "POST":
        if "create_team" in request.POST:
            create_team_form = TeamForm(request.POST)
            if team:
                create_team_form.add_error(None, "You are already in a team!")
            else:
                if create_team_form.is_valid():
                    team = create_team_form.save(commit=False)
                    team.hunt = hunt
                    team.save()
                    team.members.add(user)

                    return redirect(urls.reverse("my_team", args=[id]))
        elif "invite_member" in request.POST:
            invite_member_form = InviteMemberForm(request.POST)
            if not team:
                invite_member_form.add_error(
                    None, "You are not in a team, so you can't invite anybody!"
                )
            else:
                if invite_member_form.is_valid():
                    user_to_invite = invite_member_form.cleaned_data["user"]
                    if hunt.organizers.filter(id=user_to_invite.id).exists():
                        invite_member_form.add_error(
                            "username", "That user is an organizer!"
                        )
                    elif team.members.filter(id=user_to_invite.id).exists():
                        invite_member_form.add_error(
                            "username", "That user is already in the team!"
                        )
                    elif team.invited_members.filter(id=user_to_invite.id).exists():
                        invite_member_form.add_error(
                            "username", "That user has already been invited!"
                        )
                    else:
                        team.invited_members.add(user_to_invite)

                        return redirect(urls.reverse("my_team", args=[id]))
        elif "accept_invite" in request.POST:
            if team:
                error = (
                    "You are already in a team, so you can't accept any invitations!"
                )
            else:
                try:
                    inviting_team = Team.objects.get(id=request.POST["accept_invite"])
                    if inviting_team.invited_members.filter(id=user.id).exists():
                        inviting_team.members.add(user)
                        inviting_team.invited_members.remove(user)

                        return redirect(urls.reverse("my_team", args=[id]))
                    else:
                        error = "You don't have an invitation to that team!"
                except Team.DoesNotExist:
                    error = "You are not in a team, so you can't invite anybody!"

    return render(
        request,
        "my_team.html",
        {
            "hunt": hunt,
            "team": team,
            "error": error,
            "create_team_form": create_team_form,
            "invite_member_form": invite_member_form,
            "inviting_teams": Team.objects.filter(hunt=hunt, invited_members=user)
            if user.is_authenticated
            else [],
            "is_organizer": not user.is_anonymous
            and hunt.organizers.filter(id=user.id).exists(),
        },
    )


class PuzzleForm(forms.ModelForm):
    content = forms.CharField(widget=MarkdownTextarea, required=False)

    class Meta:
        model = Puzzle
        fields = [
            "name",
            "content",
            "answer",
            "points",
            "order",
            "progress_points",
            "progress_threshold",
        ]


@login_required
def new_puzzle(request, id):
    user = request.user
    hunt = get_object_or_404(Hunt, id=id)

    if not hunt.organizers.filter(id=user.id).exists():
        return HttpResponse(status=403)

    if request.method == "POST":
        form = PuzzleForm(request.POST)
        if form.is_valid():
            puzzle = form.save(commit=False)
            puzzle.hunt = hunt
            puzzle.save()

            return redirect(urls.reverse("view_puzzle", args=[hunt.id, puzzle.id]))
    else:
        form = PuzzleForm()

    return render(
        request,
        "new_puzzle.html",
        {
            "hunt": hunt,
            "form": form,
        },
    )


@login_required
def edit_puzzle(request, hunt_id, puzzle_id):
    user = request.user
    hunt = get_object_or_404(Hunt, id=hunt_id)
    puzzle = get_object_or_404(Puzzle, hunt=hunt, id=puzzle_id)

    if not hunt.organizers.filter(id=user.id).exists():
        return HttpResponse(status=403)

    if request.method == "POST":
        form = PuzzleForm(request.POST, instance=puzzle)
        if form.is_valid():
            puzzle = form.save()
            return redirect(urls.reverse("view_puzzle", args=[hunt.id, puzzle.id]))
    else:
        form = PuzzleForm(instance=puzzle)

    return render(
        request,
        "edit_puzzle.html",
        {
            "hunt": hunt,
            "puzzle": puzzle,
            "form": form,
        },
    )


@csrf_exempt
def preview_markdown(request):
    if request.method == "POST":
        output = render_to_string(
            "preview_markdown.html", {"input": request.body.decode("utf-8")}
        )
        return JsonResponse(
            {
                "success": True,
                "output": output,
            }
        )
    return JsonResponse(
        {
            "success": False,
            "error": "No markdown input received",
        }
    )
