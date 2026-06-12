"""AFK Journey combined game class."""

from .mixins.afk_stages import AFKStagesMixin
from .mixins.arcane_labyrinth import ArcaneLabyrinthMixin
from .mixins.arena import ArenaMixin
from .mixins.assist import AssistMixin
from .mixins.dailies import DailiesMixin
from .mixins.duras_trials import DurasTrialsMixin
from .mixins.frostfire_showdown import FrostfireShowdownMixin
from .mixins.homestead_helper import HomesteadHelperMixin
from .mixins.legend_trial import SeasonLegendTrial
from .mixins.quests import QuestMixin
from .mixins.ravaged_realm import RavagedRealmMixin
from .mixins.start_afk_journey import StartAFKJourney
from .mixins.sunlit_showdown import SunlitShowdownMixin
from .mixins.supreme_arena import SupremeArenaMixin
from .mixins.titan_reaver_proxy_battle import TitanReaverProxyBattleMixin


class AFKJourney(
    DailiesMixin,
    ArenaMixin,
    DurasTrialsMixin,
    SeasonLegendTrial,
    AFKStagesMixin,
    FrostfireShowdownMixin,
    TitanReaverProxyBattleMixin,
    StartAFKJourney,
    QuestMixin,
    SupremeArenaMixin,
    SunlitShowdownMixin,
    HomesteadHelperMixin,
    RavagedRealmMixin,
    AssistMixin,
    ArcaneLabyrinthMixin,
):
    """AFK Journey concrete game class combining all feature mixins."""
