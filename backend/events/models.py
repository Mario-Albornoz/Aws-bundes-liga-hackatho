from datetime import datetime
from typing import Any, Optional
 
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_pascal
from enum import Enum

class CaseInsensitiveEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None

class EventBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal, 
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class MatchEvent(EventBaseModel):
    """
    Represents a single <Event> element from the XML.
    """
    event_id: str
    match_id: str
    event_time: datetime
    event_type: str
    subelement: Any # model of the specific type of event

from enum import Enum

class PlayingPosition(CaseInsensitiveEnum):
    TW  = "TW"   # Goalkeeper
    LV  = "LV"   # Left-back
    IVL = "IVL"  # Centre-back (Left)
    IVZ = "IVZ"  # Centre-back
    IVR = "IVR"  # Centre-back (Right)
    RV  = "RV"   # Right-back
    DLM = "DLM"  # Defensive midfield (Left)
    DML = "DML"  # Defensive midfield (Centre Left)
    DMZ = "DMZ"  # Defensive midfield (Centre)
    DMR = "DMR"  # Defensive midfield (Centre Right)
    DRM = "DRM"  # Defensive midfield (Right)
    LM  = "LM"   # Left midfield
    HL  = "HL"   # Central midfield (Left)
    MZ  = "MZ"   # Central midfield (Centre)
    HR  = "HR"   # Central midfield (Right)
    RM  = "RM"   # Right midfield
    OLM = "OLM"  # Attacking left midfield
    OHL = "OHL"  # Attacking midfield (Centre Left)
    ZO  = "ZO"   # Attacking midfield (Centre)
    OHR = "OHR"  # Attacking midfield (Centre Right)
    ORM = "ORM"  # Attacking right midfield
    HST = "HST"  # Deep-lying forward
    LA  = "LA"   # Left wing
    STL = "STL"  # Attack (Centre Left)
    STZ = "STZ"  # Centre forward
    STR = "STR"  # Attack (Centre Right)
    RA  = "RA"   # Right wing

class GoalDisallowedReason(CaseInsensitiveEnum):
    offside = "offside"
    foul = "foul"
    handBall = "handBall"
    other = "other"

class FoulType(CaseInsensitiveEnum):
    foul = "foul"
    handBall = "handBall"
    other = "other"

class CardColor(CaseInsensitiveEnum):
    yellow = "yellow"
    yellowPenaltyShootout = "yellowPenaltyShootout"
    yellowRed = "yellowRed"
    red = "red"

class CardRating(CaseInsensitiveEnum):
    yellow = "yellow"
    canceled = "canceled"
    yellowRed = "yellowRed"
    red = "red"
    unvalued = "unvalued"

class CommittingPlayerAction(CaseInsensitiveEnum):
    slidingTackle = "slidingTackle"
    holding = "holding"
    elbowCheck = "elbowCheck"

class Side(CaseInsensitiveEnum):
    right ="right"
    left = "left"
    other = "other"
    none = "none"

class DribblingType(CaseInsensitiveEnum):
    overrun = "overrun"
    atTheFoot = "atTheFoot"

class TacklingGameRole(CaseInsensitiveEnum):
    withBallControl = "withBallControl"
    withoutBallControl = "withoutBallControl"

class TacklingGameWinnerResult(CaseInsensitiveEnum):
    dribbledAround = "dribbledAround"
    ballcontactSucceeded = "ballcontactSucceeded"
    fouled = "fouled"
    ballClaimed = "ballClaimed"
    layoff = "layoff"
    ballControlRetained = "ballControlRetained"

class TacklingGameType(CaseInsensitiveEnum): 
    ground = "ground"
    air = "air"

class TacklingGameWinnerAction(CaseInsensitiveEnum):
    goal = "goal"
    assist = "assist"
    shot = "shot"
    shotAssist = "shotAssist"

class ShotType(CaseInsensitiveEnum):
    rightLeg = "rightLeg"
    leftLeg = "leftLeg"
    head = "head"
    upperBody = "upperBody"
    noHeader = "noHeader"

class ExtendedShotType(CaseInsensitiveEnum):
    overHeadKick = "overHeadKick"
    backheel = "backheel"
    chip = "chip"
    scoop = "scoop"
    divingHeader = "divingHeader"
    frontalVolley = "frontalVolley"

class ChanceEvaluation(CaseInsensitiveEnum):
    sitter = "sitter"
    chance = "chance"
    none = "none"

class AssistAction(CaseInsensitiveEnum):
    header = "header"
    longPassFromOpenPlay = "longPassFromOpenPlay"
    otherPassFromOpenPlay = "otherPassFromOpenPlay"
    oneTwo = "oneTwo"
    crossFromOpenPlay = "crossFromOpenPlay"
    shot = "shot"
    freeKick = "freeKick"
    cornerKick = "cornerKick"
    throwIn = "throwIn"
    teammateAction = "teammateAction"
    fouled = "fouled"
    other = "other"

class TypeShot(CaseInsensitiveEnum):
    direct = "direct"
    indirect = "indirect"
    others = "others"
    freekick = "freekick"

class BallContol(CaseInsensitiveEnum):
    direct = "direct"
    volley = "volley"
    controlShot = "controlShot"
    dribblingLess10m = "dribblingLess10m"
    dribblingMore10m = "dribblingMore10m"
    setPiece = "setPiece"

class Setup(CaseInsensitiveEnum): 
    header = "header"
    longPassFromOpenPlay = "longPassFromOpenPlay"
    otherPassFromOpenPlay = "otherPassFromOpenPlay"
    oneTwo = "oneTwo"
    crossFromOpenPlay = "crossFromOpenPlay"
    shot = "shot"
    freeKick = "freeKick"
    cornerKick = "cornerKick"
    throwIn = "throwIn"
    teammateAction = "teammateAction"
    reboundWoodwork = "reboundWoodwork"
    reboundGoalkeeper = "reboundGoalkeeper"
    reboundOutfieldPlayer = "reboundOutfieldPlayer"
    reboundTeammate = "reboundTeammate"
    reboundOther = "reboundOther"
    oppositionMisplacedPass = "oppositionMisplacedPass"
    oppositionGoalkeeperAction = "oppositionGoalkeeperAction"
    oppositionDefensiveAction = "oppositionDefensiveAction"
    oppositionOtherAction = "oppositionOtherAction"
    ownSetPiece = "ownSetPiece"

class CounterAttack(CaseInsensitiveEnum):
    true = "true"
    beforePenalty = "beforeRenalty"
    false = "false"

class BuildUp(CaseInsensitiveEnum):
    crossOpenPlay = "crossOpenPlay"
    passOpenPlay = "passOpenPlay"
    freeKick = "freeKick"
    penaltyKick = "penaltyKick"
    cornerKick = "cornerKick"
    throwIn = "throwIn"
    lossOfPossession = "lossOfPossession"
    run = "run"

class SetupOrigin(CaseInsensitiveEnum):
    left = "left"
    insideLeft = "insideLeft"
    insideRight = "insideRight"
    right = "right"

class PenaltyExecution(CaseInsensitiveEnum):
    targetedShot = "targetedShot"
    powerfulShot = "powerfulShot"
    trickShot = "trickShot"

class DirectFreeKickIntention(CaseInsensitiveEnum):
    nearKeeper = "nearKeeper"
    farKeeper = "farKeeper"
    underWall = "underWall"
    secondIntendedAction = "secondIntendedAction"
    other = "other"

class ShotCondition(CaseInsensitiveEnum):
    notComplicated = "notComplicated"
    complicated = "complicated"
    veryComplicated = "veryComplicated"

class SaveType(CaseInsensitiveEnum):
    Arms = "arms"
    legs = "legs"
    others = "others"

class SaveResult(CaseInsensitiveEnum):
    held = "held"
    cleared = "cleared"
    notCleared = "notCleared"

class PostTouch(CaseInsensitiveEnum): 
    repelledToLeftPost = "repelledToLeftPost"
    repelledToRightPost = "repelledToRightPost"
    repelledToCrossbar = "repelledToCrossbar"

class Placing(CaseInsensitiveEnum):
    near = "near"
    far = "far"

class PitchMarking(CaseInsensitiveEnum):
    left = "left"
    right = "right"
    over = "over"
    sideline = "sideline"
    overCrossbarRight = "overCrossbarRight"
    overCrossbarLeft = "overCrossbarLeft"

class Location(CaseInsensitiveEnum):
    leftPost = "leftPost"
    rightPost = "rightPost"
    crossBar = "crossBar"

class Evaluation(CaseInsensitiveEnum):
    successfullyCompleted = "successfullyCompleted"
    successful = "successful"
    unsuccessful = "unsuccessful"

class Height(CaseInsensitiveEnum):
    flat = "flat"
    high = "high"

class Distance(CaseInsensitiveEnum):
    short = "short"
    medium = "medium"
    long = "long"

class GoalKeeperAction(CaseInsensitiveEnum):
    throwOut = "throwOut"
    punt = "punt"

class PlayOrigin(CaseInsensitiveEnum):
    oppositionHalf = "oppositionHalf"
    ownHalf = "ownHalf"

class Rotation(CaseInsensitiveEnum):
    towardsGoal = "towardsGoal"
    awayFromGoal = "awayFromGoal"
    other = "other"

class Direction(CaseInsensitiveEnum):
    throughBall = "throughBall"
    diagonalBall = "diagonalBall"
    squarePass = "squarePass"
    backPass = "backPass"

class OneTwo(CaseInsensitiveEnum):
    firstPasser = "firstPasser"
    secondPasser = "secondPasser"
    both = "both"

class GoalKeeperInterference(CaseInsensitiveEnum):
    caught = "caught"
    fisted = "fisted"
    rebounded = "rebounded"

class PossessionLossType(CaseInsensitiveEnum):
    tacklingGameLostWithBallPossession = "tacklingGameLostWithBallPossession"
    unsuccessfulPass = "unsuccessfulPass"
    other = "other"

class ResultFirstPenalty(CaseInsensitiveEnum):
    converted = "converted"
    notConverted = "notConverted"

class RetakeReason(CaseInsensitiveEnum):
    taker = "taker"
    goalkeeper = "goalkeeper"
    otherPlayers = "otherPlayers"
    other = "other"

class CornerKickPlacing(CaseInsensitiveEnum):
    hitOpponent = "hitOpponent"
    short = "short"
    nearPost = "nearPost"
    center = "center"
    farPost = "farPost"
    backcourt = "backcourt"
    intoTouch = "intoTouch"
    other = "other"

class PostMarking(CaseInsensitiveEnum):
    nearPost = "nearPost"
    farPost = "farPost"
    both = "both"
    none = "none"

class GameSection(CaseInsensitiveEnum):
    firstHalf = "firstHalf"
    secondHalf = "secondHalf"
    firstHalfExtra = "firstHalfExtra"
    secondHalfExtra = "secondHalfExtra"

class BallClaimimgType(CaseInsensitiveEnum):
    interceptedBall = "interceptedBall"
    block = "block"
    ballHeld = "ballHeld"
    ballClaimed = "ballClaimed"

class Substitution(EventBaseModel):
    player_out: str
    team: str
    player_in: str
    playing_position: PlayingPosition

class RefereeSubstitution(EventBaseModel):
    referee_in: str
    referee_out: str

class RefereeBall(EventBaseModel):
    pass

class GoalDisallowed(EventBaseModel):
    team: str
    player: str
    reason: GoalDisallowedReason

class OtherRefereeAction(EventBaseModel):
    reason: str
    start_time: datetime
    end_time: datetime

class Caution(EventBaseModel):
    team: str
    player: str
    card_color: CardColor
    card_rating: CardRating

class CautionTeamofficial(EventBaseModel):
    team: str
    person_sent_off: str
    unknown_person: Optional[str] = None
    card_color: CardColor

class FinalWhistle(EventBaseModel):
    game_section: str
    final_result: str
    breaking_off: bool
    reason: Optional[str] = None

class StartPenaltyShootOut(EventBaseModel):
    pass

class Offside(EventBaseModel):
    team: str
    player: str

class Foul(EventBaseModel):
    team_fouler: str
    team_fouled: str = None
    fouler: str
    fouled: str = None
    foul_type: FoulType
    committing_player_action: Optional[CommittingPlayerAction] = None

class TacklingGame(EventBaseModel):
    winner_team: str
    winner: str
    loser_team: str
    loser: str
    dribble_evaluation: Optional[str] = None
    dribbling_side: Optional[Side] = None
    dribbling_type: Optional[DribblingType] = None
    ball_possession_phase: Optional[int] = None
    goalkeeper_involved: bool = False
    winner_role: TacklingGameRole
    loser_role: TacklingGameRole
    winner_result: TacklingGameWinnerResult
    type: TacklingGameType
    possession_change: bool
    winner_action: Optional[TacklingGameWinnerAction] = None

class Nutmeg(EventBaseModel):
    team: str
    affected_team: str
    player: str
    affected_player: str

class SpectacularPlay(EventBaseModel):
    team: str
    player: str
    type: str

class OtherPlayerAction(EventBaseModel):
    team: str
    player: str
    player_becomes_goalkeeper: bool
    change_of_captain: bool
    change_contingent_exhausted: bool

class SuccessfulShot(EventBaseModel):
    extended_type_of_shot: Optional[ExtendedShotType] = None
    counter_attack: Optional[CounterAttack] = None
    solo: bool
    goal_zone: int
    current_result: str
    assist: Optional[str] = None

class SavedShot(EventBaseModel):
    save_type: SaveType
    save_result: SaveResult
    post_touch: Optional[PostTouch] = None
    goal_keeper: str
    goal_zone: int = None

class BlockedShot(EventBaseModel):
    player: str
    goal_prevented: bool
    blocked_by_own_team: bool = False
    post_touch: Optional[PostTouch] = None

class ShotWide(EventBaseModel):
    placing: Placing
    pitch_marking: PitchMarking

class ShotWoodWork(EventBaseModel):
    location: Location

class OtherShot(EventBaseModel):
    pass

class ShotAtGoal(EventBaseModel):
    team: str
    player: str
    type_of_shot: ShotType
    inside_box: bool
    chance_evaluation: ChanceEvaluation
    shot_origin: int
    ball_possession_phase: int
    assist_action: Optional[AssistAction] = None
    after_free_kick: bool
    assist_shot_at_goal: Optional[str] = None
    assist_type_shot_at_goal: Optional[TypeShot] = None
    shot_assist_fouled_player: Optional[str] = None
    taker_ball_control: BallContol
    taker_setup: Setup
    sitter_contribution: Optional[str] = None
    build_up: BuildUp
    setup_origin: SetupOrigin
    penalty_execution: Optional[PenaltyExecution] = None
    penalty_direction: Optional[int] = None
    direction_free_kick_intention: Optional[DirectFreeKickIntention] = None
    xG: Optional[float] = None
    distance_to_goal: Optional[float] = None
    angle_to_goal: Optional[float] = None
    pressure: Optional[float] = None
    player_speed: Optional[float] = None
    amount_of_defender: Optional[int] = None
    goal_distance_goalkeeper: Optional[float] = None
    shot_contribution: Optional[str] = None
    shot_condition: Optional[ShotCondition] = None
    rotation: Optional[str] = None
    subelement: Optional[SuccessfulShot | SavedShot | BlockedShot | ShotWide | ShotWoodWork | OtherShot] = None

class Pass(EventBaseModel):
    free_kick_layup: bool
    direction: Optional[Direction] = None
    one_two: Optional[OneTwo] = None

class Cross(EventBaseModel):
    goal_keeper_interference: Optional[GoalKeeperInterference] = None
    goal_keeper: Optional[str] = None
    side: Side

class Play(EventBaseModel):
    team: str
    player: str
    recipient: Optional[str] = None
    from_open_play: bool
    ball_possession_phase: int
    evaluation: Evaluation
    height: Height
    distance: Distance
    penalty_box: bool
    goal_keeper_action: Optional[GoalKeeperAction] = None
    play_origin: Optional[PlayOrigin] = None
    semi_field: bool
    flat_cross: bool
    rotation: Optional[Rotation] = None
    subelement: Optional[Pass | Cross] = None

class OwnGoal(EventBaseModel):
    team: str
    player: str
    team_own_goal_counts_for: str
    ball_possession_phase: int
    own_goal_from_counter_attack: bool
    type_of_shot: ShotType
    current_result: str
    shot_origin: int
    goal_zone: int
    scorer_ball_touch: BallContol
    scorer_setup: Setup
    build_up: BuildUp
    setup_origin: SetupOrigin

class PreventOwnGoal(EventBaseModel):
    team: str
    player: str
    save_type: SaveType
    save_result: SaveResult
    post_touch: Optional[PostTouch] = None

class PossessionLossBeforeGoal(EventBaseModel):
    team: str
    player: str
    possession_loss_origin: int
    type_of_possession_loss: PossessionLossType

class ChanceWithoutShot(EventBaseModel):
    team: str
    player: str
    prevention_goal_keeper: bool
    sitter: bool
    taker_setup: Setup
    counter_attack: bool
    situation: BuildUp
    setup_origin: SetupOrigin
    assist_action: Optional[AssistAction] = None
    chance_assist: Optional[str] = None
    chance_assist_type: Optional[TypeShot] = None
    chance_assist_fouled_player: Optional[str] = None

class Run(EventBaseModel):
    team: str
    player: str

class Fairplay(EventBaseModel):
    team: str
    player: str
    ball_possession_phase: int

class OtherBallAction(EventBaseModel):
    team: str
    player: str
    ball_possession_phase: int
    defensive_clearance: Optional[str] = None

class FaultExecution(EventBaseModel):
    team: str
    player: str
    ball_possession_phase: int

class ThrowIn(EventBaseModel):
    side: Side
    team: str
    decision_timestamp: datetime
    subelement: Optional[FaultExecution | Play | Fairplay] = None

class Penalty(EventBaseModel):
    team: str
    fouled_player: Optional[str] = None
    causing_player: str
    goalkeeper_movement: Optional[Side] = None
    retaken_penalty: bool
    player_first_penalty: Optional[str] = None
    direction_first_penalty: Optional[int] = None
    result_first_penalty: Optional[ResultFirstPenalty] = None
    retake_reason: Optional[RetakeReason] = None
    decision_timestamp: datetime
    prospective_taker: Optional[str] = None
    subelement: Optional[Play | ShotAtGoal | Fairplay] = None

class CornerKick(EventBaseModel):
    team: str
    side: Side
    placing: Optional[CornerKickPlacing] = None
    target_area: Optional[CornerKickPlacing] = None
    rotation: Optional[Rotation] = None
    post_marking: Optional[PostMarking] = None
    decision_timestamp: datetime
    subelement: Optional[Play | ShotAtGoal | Fairplay] = None

class FreeKick(EventBaseModel):
    team: str
    execution_mode: Optional[TypeShot] = None
    decision_timestamp: datetime
    subelement: Optional[Play | ShotAtGoal | Fairplay] = None

class GoalKick(EventBaseModel):
    team: str
    decision_timestamp: datetime
    subelement: Optional[Play | ShotAtGoal | Fairplay] = None

class KickOff(EventBaseModel):
    game_section: Optional[GameSection] = None
    team_left: str
    team_right: str
    subelement: Optional[Play | ShotAtGoal | Fairplay] = None

class BallClaiming(EventBaseModel):
    team: str
    player: str
    ball_possession_phase: int
    type: BallClaimimgType

class Delete(EventBaseModel):
    reason: Optional[str] = None

class VideoAssistantAction(EventBaseModel):
    linesman2: str
    opponent_team: str
    proofed_event: str
    ref_decision: str
    final_decision: str
    timestamp_start_action: datetime
    video_assistant: str
    referee: str
    team_challenged: str
    timestamp_end_action: datetime
    linesman1: str
    ref_decision_evaluation: str

class AdditionalTimeDisplayed(EventBaseModel):
    minute: str

class PlayerNotSentOff(EventBaseModel):
    team: str
    type: str
    reason: str
    player: str
    ref_decision_evaluation: str

EVENTS_REGISTRY: dict[str, type[EventBaseModel]] = {
    "Substitution": Substitution,
    "RefereeSubstitution": RefereeSubstitution,
    "RefereeBall": RefereeBall,
    "GoalDisallowed": GoalDisallowed,
    "OtherRefereeAction": OtherRefereeAction,
    "Caution": Caution,
    "CautionTeamofficial": CautionTeamofficial,
    "FinalWhistle": FinalWhistle,
    "StartPenaltyShootOut": StartPenaltyShootOut,
    "Offside": Offside,
    "Foul": Foul,
    "TacklingGame": TacklingGame,
    "Nutmeg": Nutmeg,
    "SpectacularPlay": SpectacularPlay,
    "OtherPlayerAction": OtherPlayerAction,
    "ShotAtGoal": ShotAtGoal,
    "Play": Play,
    "OwnGoal": OwnGoal,
    "PreventOwnGoal": PreventOwnGoal,
    "PossessionLossBeforeGoal": PossessionLossBeforeGoal,
    "ChanceWithoutShot": ChanceWithoutShot,
    "Run": Run,
    "Fairplay": Fairplay,
    "OtherBallAction": OtherBallAction,
    "FaultExecution": FaultExecution,
    "ThrowIn": ThrowIn,
    "Penalty": Penalty,
    "CornerKick": CornerKick,
    "FreeKick": FreeKick,
    "GoalKick": GoalKick,
    "KickOff": KickOff,
    "BallClaiming": BallClaiming,
    "Delete": Delete,
    "VideoAssistantAction": VideoAssistantAction,
    "AdditionalTimeDisplayed" : AdditionalTimeDisplayed,
    "PlayerNotSentOff": PlayerNotSentOff
}

SUBELEMENTS_REGISTRY: dict[str, type[EventBaseModel]] = {
    "ShotAtGoal": ShotAtGoal,
    "SuccessfulShot": SuccessfulShot,
    "SavedShot": SavedShot,
    "BlockedShot": BlockedShot,
    "ShotWide": ShotWide,
    "ShotWoodWork": ShotWoodWork,
    "OtherShot": OtherShot,
    "Pass": Pass,
    "Cross": Cross,
    "Play": Play,
    "Fairplay": Fairplay,
    "FaultExecution": FaultExecution,
}