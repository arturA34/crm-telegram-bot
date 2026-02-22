TEXTS: dict[str, str] = {
    # General
    "btn_back": "« Back",
    "btn_cancel": "Cancel",
    "cancelled": "Cancelled.",
    "error": "Something went wrong. Try again.",

    # Main menu
    "menu_title": "What would you like to do?",
    "btn_my_clients": "\U0001f4cb Clients",
    "btn_add_client": "\u2795 New client",
    "btn_pipeline": "\U0001f4ca Pipeline",
    "btn_stats": "\U0001f4c8 Stats",
    "btn_team": "\U0001f465 Team",
    "btn_settings": "\u2699\ufe0f Settings",

    # Start
    "welcome": "Hi, <b>{name}</b>! Choose your language:",
    "welcome_back": "Hi, <b>{name}</b>!",
    "language_set": "\u2705 English selected.",

    # Team
    "team_menu": "\U0001f465 <b>Team</b>",
    "btn_create_team": "\u2795 Create team",
    "btn_join_team": "\U0001f517 Join team",
    "btn_leave_team": "\U0001f6aa Leave team",
    "btn_members": "\U0001f4cb Members",
    "btn_remove_member": "\u274c Remove member",
    "team_enter_name": "Team name:",
    "team_created": "\u2705 <b>{name}</b> created\nInvite code: <code>{code}</code>",
    "team_enter_code": "Invite code:",
    "team_joined": "\u2705 Joined <b>{name}</b>",
    "team_left": "\u2705 Left the team.",
    "team_invalid_code": "\u274c Invalid invite code.",
    "team_already_in": "Already in a team. Leave first.",
    "team_not_in": "You're not in a team.",
    "team_owner_cant_leave": "Owner can't leave. Delete the team instead.",
    "team_members_list": "\U0001f465 <b>{name}</b>\n{members}",
    "team_member_removed": "\u2705 Member removed.",
    "team_member_not_found": "Member not found.",
    "team_select_member": "Select member to remove:",
    "team_no_members": "No other members.",
    "team_info": "<b>{name}</b>\nRole: {role} \u00b7 Members: {count}",

    # Client
    "client_enter_name": "Client name:",
    "client_enter_phone": "Phone (/skip):",
    "client_enter_source": "Lead source (/skip):",
    "client_enter_budget": "Budget (/skip):",
    "client_created": "\u2705 <b>{name}</b> added",
    "client_invalid_budget": "Enter a number or /skip:",
    "client_detail": (
        "<b>{name}</b>\n"
        "\U0001f4de {phone}  \u00b7  \U0001f4cd {source}\n"
        "\U0001f4b0 {budget}  \u00b7  {status}\n"
        "\U0001f464 {manager}  \u00b7  \U0001f514 {reminder}\n"
        "<i>{created}</i>"
    ),
    "client_updated": "\u2705 Updated.",
    "client_deleted": "\u2705 Deleted.",
    "client_not_found": "Client not found.",
    "client_access_denied": "Access denied.",
    "btn_edit_client": "\u270f\ufe0f Edit",
    "btn_delete_client": "\U0001f5d1 Delete",
    "btn_change_status": "\U0001f504 Status",
    "btn_set_reminder": "\U0001f514 Reminder",
    "client_select_field": "Edit field:",
    "btn_edit_name": "Name",
    "btn_edit_phone": "Phone",
    "btn_edit_source": "Source",
    "btn_edit_budget": "Budget",
    "client_enter_new_value": "New value:",
    "client_confirm_delete": "Delete <b>{name}</b>?",
    "btn_confirm_yes": "\u2705 Yes",
    "btn_confirm_no": "\u274c No",
    "client_select_status": "New status:",
    "client_status_changed": "Status \u2192 <b>{status}</b>",
    "client_list_empty": "No clients yet.",
    "client_list_title": "<b>{status}</b>",

    # Pipeline
    "pipeline_title": "\U0001f4ca <b>Pipeline</b>",

    # Stats
    "stats_title": "\U0001f4c8 <b>Stats</b>",
    "stats_total": "Total: {total}",
    "stats_won": "\u2705 Won: {won}",
    "stats_lost": "\u274c Lost: {lost}",
    "stats_in_progress": "\u23f3 Active: {in_progress}",
    "stats_revenue": "\U0001f4b0 Revenue: {revenue}",
    "stats_conversion": "\U0001f3af Conversion: {conversion}%",
    "leaderboard_title": "\U0001f3c6 <b>Leaderboard</b>",
    "leaderboard_line": "{rank}. {name} \u2014 {score} pts",
    "leaderboard_no_team": "Join a team to see the leaderboard.",

    # Reminder
    "reminder_enter_date": "Date (DD.MM.YYYY):",
    "reminder_enter_time": "Time (HH:MM):",
    "reminder_set": "\U0001f514 Reminder set: {datetime}",
    "reminder_invalid_date": "Invalid date. Use DD.MM.YYYY:",
    "reminder_invalid_time": "Invalid time. Use HH:MM:",
    "reminder_notification": (
        "\U0001f514 <b>{name}</b>\n"
        "{status} \u00b7 {phone}"
    ),
    "reminder_none": "\u2014",

    # Status labels
    "status_NEW": "\U0001f7e2 New",
    "status_IN_PROGRESS": "\U0001f7e1 In Progress",
    "status_PROPOSAL_SENT": "\U0001f7e0 Proposal Sent",
    "status_WON": "\u2705 Won",
    "status_LOST": "\u274c Lost",

    # Role labels
    "role_SOLO": "Solo",
    "role_OWNER": "Owner",
    "role_MANAGER": "Manager",

    # Settings
    "settings_menu": "\u2699\ufe0f <b>Settings</b>",
}
