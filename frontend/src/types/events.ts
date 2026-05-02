export type PlayingPosition =
    | 'TW' | 'LV' | 'IVL' | 'IVZ' | 'IVR' | 'RV'
    | 'DLM' | 'DML' | 'DMZ' | 'DMR' | 'DRM'
    | 'LM' | 'HL' | 'MZ' | 'HR' | 'RM'
    | 'OLM' | 'OHL' | 'ZO' | 'OHR' | 'ORM'
    | 'HST' | 'LA' | 'STL' | 'STZ' | 'STR' | 'RA';

export type GoalDisallowedReason = 'offside' | 'foul' | 'handBall' | 'other';

export type FoulType = 'foul' | 'handBall' | 'other';

export type CardColor =
    | 'yellow'
    | 'yellowPenaltyShootout'
    | 'yellowRed'
    | 'red';

export type CardRating =
    | 'yellow'
    | 'canceled'
    | 'yellowRed'
    | 'red'
    | 'unvalued';

export type CommittingPlayerAction =
    | 'slidingTackle'
    | 'holding'
    | 'elbowCheck';

export type Side = 'right' | 'left' | 'other' | 'none';

export type DribblingType = 'overrun' | 'atTheFoot';

export type TacklingGameRole =
    | 'withBallControl'
    | 'withoutBallControl';

export type TacklingGameWinnerResult =
    | 'dribbledAround'
    | 'ballcontactSucceeded'
    | 'fouled'
    | 'ballClaimed'
    | 'layoff'
    | 'ballControlRetained';

export type TacklingGameType = 'ground' | 'air';

export type TacklingGameWinnerAction =
    | 'goal'
    | 'assist'
    | 'shot'
    | 'shotAssist';

export type ShotType =
    | 'rightLeg'
    | 'leftLeg'
    | 'head'
    | 'upperBody'
    | 'noHeader';

export type ExtendedShotType =
    | 'overHeadKick'
    | 'backheel'
    | 'chip'
    | 'scoop'
    | 'divingHeader'
    | 'frontalVolley';

export type ChanceEvaluation = 'sitter' | 'chance' | 'none';

export type AssistAction =
    | 'header'
    | 'longPassFromOpenPlay'
    | 'otherPassFromOpenPlay'
    | 'oneTwo'
    | 'crossFromOpenPlay'
    | 'shot'
    | 'freeKick'
    | 'cornerKick'
    | 'throwIn'
    | 'teammateAction'
    | 'fouled'
    | 'other';

export type TypeShot = 'direct' | 'indirect' | 'others' | 'freekick';

export type BallControl =
    | 'direct'
    | 'volley'
    | 'controlShot'
    | 'dribblingLess10m'
    | 'dribblingMore10m'
    | 'setPiece';

export type Setup =
    | 'header'
    | 'longPassFromOpenPlay'
    | 'otherPassFromOpenPlay'
    | 'oneTwo'
    | 'crossFromOpenPlay'
    | 'shot'
    | 'freeKick'
    | 'cornerKick'
    | 'throwIn'
    | 'teammateAction'
    | 'reboundWoodwork'
    | 'reboundGoalkeeper'
    | 'reboundOutfieldPlayer'
    | 'reboundTeammate'
    | 'reboundOther'
    | 'oppositionMisplacedPass'
    | 'oppositionGoalkeeperAction'
    | 'oppositionDefensiveAction'
    | 'oppositionOtherAction'
    | 'ownSetPiece';

export type CounterAttack = 'true' | 'beforeRenalty' | 'false';

export type BuildUp =
    | 'crossOpenPlay'
    | 'passOpenPlay'
    | 'freeKick'
    | 'penaltyKick'
    | 'cornerKick'
    | 'throwIn'
    | 'lossOfPossession'
    | 'run';

export type SetupOrigin =
    | 'left'
    | 'insideLeft'
    | 'insideRight'
    | 'right';

export type PenaltyExecution =
    | 'targetedShot'
    | 'powerfulShot'
    | 'trickShot';

export type DirectFreeKickIntention =
    | 'nearKeeper'
    | 'farKeeper'
    | 'underWall'
    | 'secondIntendedAction'
    | 'other';

export type ShotCondition =
    | 'notComplicated'
    | 'complicated'
    | 'veryComplicated';

export type SaveType = 'arms' | 'legs' | 'others';

export type SaveResult = 'held' | 'cleared' | 'notCleared';

export type PostTouch =
    | 'repelledToLeftPost'
    | 'repelledToRightPost'
    | 'repelledToCrossbar';

export type Placing = 'near' | 'far';

export type PitchMarking =
    | 'left'
    | 'right'
    | 'over'
    | 'sideline'
    | 'overCrossbarRight'
    | 'overCrossbarLeft';

export type Location = 'leftPost' | 'rightPost' | 'crossBar';

export type Evaluation =
    | 'successfullyCompleted'
    | 'successful'
    | 'unsuccessful';

export type Height = 'flat' | 'high';

export type Distance = 'short' | 'medium' | 'long';

export type GoalKeeperAction = 'throwOut' | 'punt';

export type PlayOrigin = 'oppositionHalf' | 'ownHalf';

export type Rotation = 'towardsGoal' | 'awayFromGoal' | 'other';

export type Direction =
    | 'throughBall'
    | 'diagonalBall'
    | 'squarePass'
    | 'backPass';

export type OneTwo = 'firstPasser' | 'secondPasser' | 'both';

export type GoalKeeperInterference = 'caught' | 'fisted' | 'rebounded';

export type PossessionLossType =
    | 'tacklingGameLostWithBallPossession'
    | 'unsuccessfulPass'
    | 'other';

export type ResultFirstPenalty = 'converted' | 'notConverted';

export type RetakeReason =
    | 'taker'
    | 'goalkeeper'
    | 'otherPlayers'
    | 'other';

export type CornerKickPlacing =
    | 'hitOpponent'
    | 'short'
    | 'nearPost'
    | 'center'
    | 'farPost'
    | 'backcourt'
    | 'intoTouch'
    | 'other';

export type PostMarking = 'nearPost' | 'farPost' | 'both' | 'none';

export type GameSection =
    | 'firstHalf'
    | 'secondHalf'
    | 'firstHalfExtra'
    | 'secondHalfExtra';

export type BallClaimingType =
    | 'interceptedBall'
    | 'block'
    | 'ballHeld'
    | 'ballClaimed';

export interface SuccessfulShot {
    extended_type_of_shot?: ExtendedShotType;
    counter_attack?: CounterAttack;
    solo: boolean;
    goal_zone: number;
    current_result: string;   
    assist?: string;          
}

export interface SavedShot {
    save_type: SaveType;
    save_result: SaveResult;
    post_touch?: PostTouch;
    goal_keeper: string;
    goal_zone?: number;
}

export interface BlockedShot {
    player: string;
    goal_prevented: boolean;
    blocked_by_own_team: boolean;
    post_touch?: PostTouch;
}

export interface ShotWide {
    placing: Placing;
    pitch_marking: PitchMarking;
}

export interface ShotWoodWork {
    location: Location;
}

export interface OtherShot { }

export type ShotSubelement =
    | SuccessfulShot
    | SavedShot
    | BlockedShot
    | ShotWide
    | ShotWoodWork
    | OtherShot;

export interface Pass {
    free_kick_layup: boolean;
    direction?: Direction;
    one_two?: OneTwo;
}

export interface Cross {
    goal_keeper_interference?: GoalKeeperInterference;
    goal_keeper?: string;
    side: Side;
}

export type PlaySubelement = Pass | Cross;

export interface FaultExecution {
    team: string;
    player: string;
    ball_possession_phase: number;
}

export interface Fairplay {
    team: string;
    player: string;
    ball_possession_phase: number;
}

export interface Substitution {
    player_out: string;
    team: string;
    player_in: string;
    playing_position: PlayingPosition;
}

export interface RefereeSubstitution {
    referee_in: string;
    referee_out: string;
}

export interface RefereeBall { }

export interface GoalDisallowed {
    team: string;
    player: string;
    reason: GoalDisallowedReason;
}

export interface OtherRefereeAction {
    reason: string;
    start_time: string;
    end_time: string;
}

export interface Caution {
    team: string;
    player: string;
    card_color: CardColor;
    card_rating: CardRating;
}

export interface CautionTeamofficial {
    team: string;
    person_sent_off: string;
    unknown_person?: string;
    card_color: CardColor;
}

export interface FinalWhistle {
    game_section: string;
    final_result: string;
    breaking_off: boolean;
    reason?: string;
}

export interface StartPenaltyShootOut { }

export interface Offside {
    team: string;
    player: string;
}

export interface Foul {
    team_fouler: string;
    team_fouled?: string;
    fouler: string;
    fouled?: string;
    foul_type: FoulType;
    committing_player_action?: CommittingPlayerAction;
}

export interface TacklingGame {
    winner_team: string;
    winner: string;
    loser_team: string;
    loser: string;
    dribble_evaluation?: string;
    dribbling_side?: Side;
    dribbling_type?: DribblingType;
    ball_possession_phase?: number;
    goalkeeper_involved: boolean;
    winner_role: TacklingGameRole;
    loser_role: TacklingGameRole;
    winner_result: TacklingGameWinnerResult;
    type: TacklingGameType;
    possession_change: boolean;
    winner_action?: TacklingGameWinnerAction;
}

export interface Nutmeg {
    team: string;
    affected_team: string;
    player: string;
    affected_player: string;
}

export interface SpectacularPlay {
    team: string;
    player: string;
    type: string;
}

export interface OtherPlayerAction {
    team: string;
    player: string;
    player_becomes_goalkeeper: boolean;
    change_of_captain: boolean;
    change_contingent_exhausted: boolean;
}

export interface ShotAtGoal {
    team: string;
    player: string;
    type_of_shot: ShotType;
    inside_box: boolean;
    chance_evaluation: ChanceEvaluation;
    shot_origin: number;
    ball_possession_phase: number;
    assist_action?: AssistAction;
    after_free_kick: boolean;
    assist_shot_at_goal?: string;
    assist_type_shot_at_goal?: TypeShot;
    shot_assist_fouled_player?: string;
    taker_ball_control: BallControl;
    taker_setup: Setup;
    sitter_contribution?: string;
    build_up: BuildUp;
    setup_origin: SetupOrigin;
    penalty_execution?: PenaltyExecution;
    penalty_direction?: number;
    direction_free_kick_intention?: DirectFreeKickIntention;
    xG?: number;
    distance_to_goal?: number;
    angle_to_goal?: number;
    pressure?: number;
    player_speed?: number;
    amount_of_defender?: number;
    goal_distance_goalkeeper?: number;
    shot_contribution?: string;
    shot_condition?: ShotCondition;
    rotation?: string;
    subelement?: ShotSubelement;
}

export interface Play {
    team: string;
    player: string;
    recipient?: string;
    from_open_play: boolean;
    ball_possession_phase: number;
    evaluation: Evaluation;
    height: Height;
    distance: Distance;
    penalty_box: boolean;
    goal_keeper_action?: GoalKeeperAction;
    play_origin?: PlayOrigin;
    semi_field: boolean;
    flat_cross: boolean;
    rotation?: Rotation;
    subelement?: PlaySubelement;
}

export interface OwnGoal {
    team: string;
    player: string;
    team_own_goal_counts_for: string;
    ball_possession_phase: number;
    own_goal_from_counter_attack: boolean;
    type_of_shot: ShotType;
    current_result: string;
    shot_origin: number;
    goal_zone: number;
    scorer_ball_touch: BallControl;
    scorer_setup: Setup;
    build_up: BuildUp;
    setup_origin: SetupOrigin;
}

export interface PreventOwnGoal {
    team: string;
    player: string;
    save_type: SaveType;
    save_result: SaveResult;
    post_touch?: PostTouch;
}

export interface PossessionLossBeforeGoal {
    team: string;
    player: string;
    possession_loss_origin: number;
    type_of_possession_loss: PossessionLossType;
}

export interface ChanceWithoutShot {
    team: string;
    player: string;
    prevention_goal_keeper: boolean;
    sitter: boolean;
    taker_setup: Setup;
    counter_attack: boolean;
    situation: BuildUp;
    setup_origin: SetupOrigin;
    assist_action?: AssistAction;
    chance_assist?: string;
    chance_assist_type?: TypeShot;
    chance_assist_fouled_player?: string;
}

export interface Run {
    team: string;
    player: string;
}

export interface OtherBallAction {
    team: string;
    player: string;
    ball_possession_phase: number;
    defensive_clearance?: string;
}

export interface ThrowIn {
    side: Side;
    team: string;
    decision_timestamp: string;
    subelement?: FaultExecution | Play | Fairplay;
}

export interface Penalty {
    team: string;
    fouled_player?: string;
    causing_player: string;
    goalkeeper_movement?: Side;
    retaken_penalty: boolean;
    player_first_penalty?: string;
    direction_first_penalty?: number;
    result_first_penalty?: ResultFirstPenalty;
    retake_reason?: RetakeReason;
    decision_timestamp: string;
    prospective_taker?: string;
    subelement?: Play | ShotAtGoal | Fairplay;
}

export interface CornerKick {
    team: string;
    side: Side;
    placing?: CornerKickPlacing;
    target_area?: CornerKickPlacing;
    rotation?: Rotation;
    post_marking?: PostMarking;
    decision_timestamp: string;
    subelement?: Play | ShotAtGoal | Fairplay;
}

export interface FreeKick {
    team: string;
    execution_mode?: TypeShot;
    decision_timestamp: string;
    subelement?: Play | ShotAtGoal | Fairplay;
}

export interface GoalKick {
    team: string;
    decision_timestamp: string;
    subelement?: Play | ShotAtGoal | Fairplay;
}

export interface KickOff {
    game_section?: GameSection;
    team_left: string;
    team_right: string;
    subelement?: Play | ShotAtGoal | Fairplay;
}

export interface BallClaiming {
    team: string;
    player: string;
    ball_possession_phase: number;
    type: BallClaimingType;
}

export interface Delete {
    reason?: string;
}

export interface VideoAssistantAction {
    linesman2: string;
    opponent_team: string;
    proofed_event: string;
    ref_decision: string;
    final_decision: string;
    timestamp_start_action: string;
    video_assistant: string;
    referee: string;
    team_challenged: string;
    timestamp_end_action: string;
    linesman1: string;
    ref_decision_evaluation: string;
}

export interface AdditionalTimeDisplayed {
    minute: string;
}

export interface PlayerNotSentOff {
    team: string;
    type: string;
    reason: string;
    player: string;
    ref_decision_evaluation: string;
}

export type EventDetail =
    | Substitution
    | RefereeSubstitution
    | RefereeBall
    | GoalDisallowed
    | OtherRefereeAction
    | Caution
    | CautionTeamofficial
    | FinalWhistle
    | StartPenaltyShootOut
    | Offside
    | Foul
    | TacklingGame
    | Nutmeg
    | SpectacularPlay
    | OtherPlayerAction
    | ShotAtGoal
    | Play
    | OwnGoal
    | PreventOwnGoal
    | PossessionLossBeforeGoal
    | ChanceWithoutShot
    | Run
    | Fairplay
    | OtherBallAction
    | FaultExecution
    | ThrowIn
    | Penalty
    | CornerKick
    | FreeKick
    | GoalKick
    | KickOff
    | BallClaiming
    | Delete
    | VideoAssistantAction
    | AdditionalTimeDisplayed
    | PlayerNotSentOff;

export interface MatchEvent {
    event_id: string;
    match_id: string;
    event_time: string;
    event_type: string;
    subelement: EventDetail | null;
}