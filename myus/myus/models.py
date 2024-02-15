from django.db import models

from django.contrib.auth.models import AbstractUser

from django.db.models import OuterRef, Exists, Sum, Q

from django.core.validators import MinValueValidator

import django.urls as urls

DEFAULT_GUESS_LIMIT = 20


class User(AbstractUser):
    display_name = models.CharField(max_length=500, blank=True, help_text="Optional.")
    discord_username = models.CharField(
        max_length=500,
        blank=True,
        help_text="Your Discord username and tag (e.g. example). Not currently used for anything, but might be used in Discord integrations if they are implemented, since it appears that many hunts in the target audience are run over Discord.",
    )
    bio = models.TextField(blank=True, help_text="Tell us about yourself. Optional.")
    creation_time = models.DateTimeField(auto_now_add=True)


class Hunt(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(help_text="Description of the hunt.")
    creation_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Start time of the hunt. If empty, the hunt will never begin. For indefinitely open hunts, you can just set it to any time in the past.",
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="End date of the hunt. If empty, the hunt will always be open.",
    )
    organizers = models.ManyToManyField(User, related_name="organizing_hunts")
    invited_organizers = models.ManyToManyField(
        User, blank=True, related_name="invited_organizing_hunts"
    )
    progress_floor = models.IntegerField(
        default=0,
        help_text="A floor on the number of 'progress points' held by every team; their 'progress points' will be computed as the maximum of this quantity and the total number of progress points granted by puzzles they've solved. Expected usage is to increase this midhunt to gradually unlock puzzles for everybody.",
        validators=[MinValueValidator(0)],
    )
    member_limit = models.IntegerField(
        default=0,
        help_text="The maximum number of members allowed per team; 0 means unlimited",
        validators=[MinValueValidator(0)],
    )
    guess_limit = models.IntegerField(
        default=DEFAULT_GUESS_LIMIT,
        help_text="The default number of guesses teams get on each puzzle; 0 means unlimited",
        validators=[MinValueValidator(0)],
    )

    def public_puzzles(self):
        return self.puzzles.filter(progress_threshold__lte=self.progress_floor)


class Puzzle(models.Model):
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE, related_name="puzzles")
    name = models.CharField(max_length=500)
    content = models.TextField(
        blank=True,
        help_text="The puzzle body. For most puzzles, we suggest just providing an external URL; however, you can put short text-only puzzles here, or include a small amount of flavortext or explanatory text with a URL.",
    )
    answer = models.CharField(max_length=500)
    points = models.IntegerField(
        default=1,
        help_text="How many points solving this puzzle earns.",
        validators=[MinValueValidator(0)],
    )
    order = models.IntegerField(
        default=0,
        help_text="Order in which this puzzle is displayed on the hunt page. Ties will be broken by puzzle name.",
    )
    progress_points = models.IntegerField(
        default=0,
        help_text="How many 'progress points' solving this puzzle earns. Progress points are only used to determine unlocking of puzzles.",
        validators=[MinValueValidator(0)],
    )
    progress_threshold = models.IntegerField(
        default=0,
        help_text="How many 'progress points' are necessary for a team to unlock this puzzle. In particular, puzzles with progress threshold ≤ the 'progress floor' of the hunt are public. (At the start of the hunt, the 'progress floor' will probably be 0 and puzzles with progress threshold 0 will be public.)",
        validators=[MinValueValidator(0)],
    )

    def is_viewable_by(self, team):
        if team:
            progress = team.progress()
        else:
            progress = self.hunt.progress_floor

        return progress >= self.progress_threshold


class GuessResponse(models.Model):
    """Any special response to a particular answer guess.

    Common use cases include some kind of "Keep going!" message in
    response to answers that are close but incorrect, or some kind of
    acknowledgement for an intermediate cluephrase asking the teams
    to do something telling teams that they should in fact do that
    thing.
    """

    puzzle = models.ForeignKey(
        Puzzle, on_delete=models.CASCADE, related_name="guess_responses"
    )
    guess = models.CharField(max_length=500)
    response = models.TextField()

    class Meta:
        unique_together = ("puzzle", "guess")


class Team(models.Model):
    # TODO: Should we have a team captain?
    name = models.CharField(max_length=500)
    hunt = models.ForeignKey(Hunt, on_delete=models.CASCADE, related_name="teams")
    members = models.ManyToManyField(
        User, blank=True, related_name="teams"
    )  # blank=True in case all members quit a team to join another one or something
    invited_members = models.ManyToManyField(
        User, blank=True, related_name="invited_teams"
    )
    creation_time = models.DateTimeField(auto_now_add=True)

    def progress(self):
        puzzles = self.hunt.puzzles
        team_progress = (
            puzzles.annotate(
                solved=Exists(
                    Guess.objects.filter(team=self, puzzle=OuterRef("pk"), correct=True)
                ),
            )
            .filter(solved=True)
            .aggregate(sum=Sum("progress_points"))["sum"]
        )
        if team_progress is None:
            team_progress = 0
        hunt_progress = self.hunt.progress_floor

        return max(team_progress, hunt_progress)

    def unlocked_puzzles(self):
        return self.hunt.puzzles.filter(progress_threshold__lte=self.progress())

    def unlocked_puzzles_with_solved(self):
        return self.unlocked_puzzles().annotate(
            solved=Exists(
                Guess.objects.filter(team=self, puzzle=OuterRef("pk"), correct=True)
            ),
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_team_name_per_hunt", fields=["name", "hunt"]
            ),
        ]


class Guess(models.Model):
    guess = models.CharField(max_length=500)
    team = models.ForeignKey(Team, related_name="guesses", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name="guesses", on_delete=models.SET_NULL, null=True
    )  # Not a source of truth because users could move around teams, but maybe useful for auditing
    puzzle = models.ForeignKey(Puzzle, related_name="guesses", on_delete=models.CASCADE)
    correct = models.BooleanField()
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_correct_guess_team_puzzle",
                fields=["team", "puzzle"],
                condition=Q(correct=True),
            )
        ]


class ExtraGuessGrant(models.Model):
    "Extra guesses granted to a particular team."

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    extra_guesses = (
        models.IntegerField()
    )  # I guess you *could* want to take guesses away...

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="unique_team_puzzle_grant", fields=["team", "puzzle"]
            ),
        ]
