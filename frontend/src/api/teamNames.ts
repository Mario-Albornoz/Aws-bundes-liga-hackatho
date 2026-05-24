/**
 * Display-name map for the anonymised club IDs in the demo dataset.
 * Mirrors the backend TeamInfo.py mapping so the frontend can show human-
 * readable names without a separate API call.
 */
export const TEAM_NAMES: Record<string, string> = {
  "DFL-CLU-000001": "Hamburg",
  "DFL-CLU-000002": "Bayern",
};

/** Return a display name for a team, falling back to the last ID segment. */
export function getTeamName(teamId: string): string {
  if (!teamId) return "—";
  return TEAM_NAMES[teamId] ?? teamId.split("-").pop() ?? teamId;
}
