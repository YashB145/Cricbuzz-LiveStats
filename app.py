import os
import streamlit as st
import requests
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ml_model import get_model_bundle, predict_match
from sql_queries import (
    query_1_all_matches, query_2_total_matches, query_3_matches_by_status,
    query_4_team1_matches, query_5_recent_matches, query_6_all_teams,
    query_7_all_players_with_teams, query_8_team_player_count, query_9_venues_by_country,
    query_10_batsmen_only, query_11_bowlers_only, query_12_all_rounders,
    query_13_venue_capacity_analysis, query_14_players_by_nationality, query_15_team_captains,
    query_16_enhanced_matches_overview, query_17_matches_by_venue, query_18_player_roles_distribution,
    query_19_teams_with_most_players, query_20_venues_by_pitch_type, query_21_players_without_team,
    query_22_matches_without_venue, query_23_complete_team_info, query_24_venue_match_analysis,
    query_25_comprehensive_database_summary
)
from crud_operations import (
    create_match, read_all_matches, read_match_by_id, read_matches_by_team,
    read_matches_by_status, read_unique_teams, read_unique_statuses,
    update_match, update_match_score, update_match_status,
    delete_match, delete_matches_by_status, get_database_stats,
    create_team, read_all_teams, update_team, delete_team,
    create_venue, read_all_venues,
    create_player, read_all_players, read_players_by_team,
    create_enhanced_match, read_all_enhanced_matches
)

# ---------------- PLAYER STATS FUNCTION ----------------
INTERNATIONAL_PLAYERS_DATA = {
    # --- MEN'S INTERNATIONAL ---
    "Virat Kohli": {
        "gender": "Men's",
        "country": "India",
        "role": "Top-order Batsman",
        "teams": ["India", "Royal Challengers Bengaluru"],
        "batting_career": {
            "Test": {"matches": 113, "innings": 191, "runs": 8848, "highest": "254*", "average": 49.15, "strike_rate": 55.56, "100s": 29, "50s": 30},
            "ODI": {"matches": 292, "innings": 280, "runs": 13848, "highest": "183", "average": 58.67, "strike_rate": 93.58, "100s": 50, "50s": 72},
            "T20I": {"matches": 125, "innings": 117, "runs": 4188, "highest": "122*", "average": 48.69, "strike_rate": 137.04, "100s": 1, "50s": 38}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 3.0},
            "ODI": {"wickets": 5, "best": "1/15", "average": 133.0, "economy": 6.22},
            "T20I": {"wickets": 4, "best": "1/13", "average": 51.0, "economy": 8.16}
        }
    },
    "Rohit Sharma": {
        "gender": "Men's",
        "country": "India",
        "role": "Opening Batsman",
        "teams": ["India", "Mumbai Indians"],
        "batting_career": {
            "Test": {"matches": 59, "innings": 101, "runs": 4137, "highest": "212", "average": 45.46, "strike_rate": 56.40, "100s": 12, "50s": 17},
            "ODI": {"matches": 262, "innings": 254, "runs": 10709, "highest": "264", "average": 49.12, "strike_rate": 91.97, "100s": 31, "50s": 55},
            "T20I": {"matches": 159, "innings": 151, "runs": 4231, "highest": "121*", "average": 32.05, "strike_rate": 140.89, "100s": 5, "50s": 32}
        },
        "bowling_career": {
            "Test": {"wickets": 2, "best": "1/26", "average": 112.0, "economy": 3.86},
            "ODI": {"wickets": 9, "best": "2/27", "average": 64.33, "economy": 5.21},
            "T20I": {"wickets": 1, "best": "1/22", "average": 113.0, "economy": 8.69}
        }
    },
    "Jasprit Bumrah": {
        "gender": "Men's",
        "country": "India",
        "role": "Fast Bowler",
        "teams": ["India", "Mumbai Indians"],
        "batting_career": {
            "Test": {"matches": 36, "innings": 58, "runs": 284, "highest": "35", "average": 7.47, "strike_rate": 45.22, "100s": 0, "50s": 0},
            "ODI": {"matches": 89, "innings": 40, "runs": 65, "highest": "16", "average": 5.00, "strike_rate": 62.50, "100s": 0, "50s": 0},
            "T20I": {"matches": 70, "innings": 12, "runs": 8, "highest": "7", "average": 4.00, "strike_rate": 61.53, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 159, "best": "6/27", "average": 20.69, "economy": 2.74},
            "ODI": {"wickets": 149, "best": "6/19", "average": 23.55, "economy": 4.59},
            "T20I": {"wickets": 89, "best": "3/7", "average": 17.74, "economy": 6.27}
        }
    },
    "Joe Root": {
        "gender": "Men's",
        "country": "England",
        "role": "Top-order Batsman",
        "teams": ["England", "Yorkshire"],
        "batting_career": {
            "Test": {"matches": 143, "innings": 261, "runs": 12402, "highest": "254", "average": 50.62, "strike_rate": 56.70, "100s": 34, "50s": 64},
            "ODI": {"matches": 171, "innings": 160, "runs": 6522, "highest": "133*", "average": 47.60, "strike_rate": 86.79, "100s": 16, "50s": 39},
            "T20I": {"matches": 32, "innings": 30, "runs": 893, "highest": "90*", "average": 35.72, "strike_rate": 126.30, "100s": 0, "50s": 5}
        },
        "bowling_career": {
            "Test": {"wickets": 70, "best": "5/8", "average": 44.57, "economy": 3.12},
            "ODI": {"wickets": 27, "best": "3/52", "average": 58.74, "economy": 5.76},
            "T20I": {"wickets": 6, "best": "2/9", "average": 22.16, "economy": 8.78}
        }
    },
    "Pat Cummins": {
        "gender": "Men's",
        "country": "Australia",
        "role": "Fast Bowler / Captain",
        "teams": ["Australia", "Sunrisers Hyderabad", "New South Wales"],
        "batting_career": {
            "Test": {"matches": 62, "innings": 98, "runs": 1295, "highest": "64*", "average": 16.39, "strike_rate": 45.82, "100s": 0, "50s": 3},
            "ODI": {"matches": 88, "innings": 57, "runs": 456, "highest": "36", "average": 12.66, "strike_rate": 78.48, "100s": 0, "50s": 0},
            "T20I": {"matches": 52, "innings": 22, "runs": 147, "highest": "28", "average": 10.50, "strike_rate": 128.94, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 269, "best": "6/23", "average": 22.53, "economy": 2.76},
            "ODI": {"wickets": 141, "best": "5/70", "average": 28.02, "economy": 5.22},
            "T20I": {"wickets": 66, "best": "3/15", "average": 23.36, "economy": 7.37}
        }
    },
    "Babar Azam": {
        "gender": "Men's",
        "country": "Pakistan",
        "role": "Top-order Batsman",
        "teams": ["Pakistan", "Peshawar Zalmi"],
        "batting_career": {
            "Test": {"matches": 54, "innings": 98, "runs": 3962, "highest": "196", "average": 44.51, "strike_rate": 54.89, "100s": 9, "50s": 26},
            "ODI": {"matches": 117, "innings": 114, "runs": 5729, "highest": "158", "average": 56.72, "strike_rate": 88.75, "100s": 19, "50s": 32},
            "T20I": {"matches": 123, "innings": 116, "runs": 4145, "highest": "122", "average": 41.03, "strike_rate": 129.08, "100s": 3, "50s": 36}
        },
        "bowling_career": {
            "Test": {"wickets": 2, "best": "1/1", "average": 22.0, "economy": 2.75},
            "ODI": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 7.00},
            "T20I": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 9.00}
        }
    },
    "Kane Williamson": {
        "gender": "Men's",
        "country": "New Zealand",
        "role": "Top-order Batsman",
        "teams": ["New Zealand", "Northern Districts"],
        "batting_career": {
            "Test": {"matches": 100, "innings": 176, "runs": 8743, "highest": "251", "average": 54.98, "strike_rate": 51.41, "100s": 32, "50s": 34},
            "ODI": {"matches": 165, "innings": 157, "runs": 6810, "highest": "148", "average": 48.64, "strike_rate": 81.18, "100s": 13, "50s": 45},
            "T20I": {"matches": 93, "innings": 90, "runs": 2575, "highest": "95", "average": 33.44, "strike_rate": 123.08, "100s": 0, "50s": 18}
        },
        "bowling_career": {
            "Test": {"wickets": 30, "best": "4/44", "average": 40.50, "economy": 3.01},
            "ODI": {"wickets": 37, "best": "4/22", "average": 35.40, "economy": 5.37},
            "T20I": {"wickets": 6, "best": "2/16", "average": 27.33, "economy": 7.34}
        }
    },
    "Rashid Khan": {
        "gender": "Men's",
        "country": "Afghanistan",
        "role": "Leg-spinner / All-rounder",
        "teams": ["Afghanistan", "Gujarat Titans"],
        "batting_career": {
            "Test": {"matches": 5, "innings": 7, "runs": 106, "highest": "51", "average": 15.14, "strike_rate": 78.51, "100s": 0, "50s": 1},
            "ODI": {"matches": 103, "innings": 82, "runs": 1322, "highest": "60*", "average": 19.44, "strike_rate": 104.92, "100s": 0, "50s": 5},
            "T20I": {"matches": 93, "innings": 54, "runs": 460, "highest": "48*", "average": 14.37, "strike_rate": 131.05, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 34, "best": "7/137", "average": 22.35, "economy": 2.97},
            "ODI": {"wickets": 190, "best": "7/18", "average": 20.03, "economy": 4.21},
            "T20I": {"wickets": 152, "best": "5/3", "average": 14.12, "economy": 6.07}
        }
    },
    "Kagiso Rabada": {
        "gender": "Men's",
        "country": "South Africa",
        "role": "Fast Bowler",
        "teams": ["South Africa", "Punjab Kings"],
        "batting_career": {
            "Test": {"matches": 64, "innings": 101, "runs": 974, "highest": "47", "average": 12.02, "strike_rate": 44.80, "100s": 0, "50s": 0},
            "ODI": {"matches": 101, "innings": 48, "runs": 381, "highest": "31*", "average": 12.70, "strike_rate": 74.41, "100s": 0, "50s": 0},
            "T20I": {"matches": 65, "innings": 22, "runs": 155, "highest": "22", "average": 15.50, "strike_rate": 113.13, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 291, "best": "7/112", "average": 22.05, "economy": 3.42},
            "ODI": {"wickets": 157, "best": "6/16", "average": 27.77, "economy": 5.09},
            "T20I": {"wickets": 71, "best": "3/18", "average": 28.53, "economy": 8.35}
        }
    },
    "Wanindu Hasaranga": {
        "gender": "Men's",
        "country": "Sri Lanka",
        "role": "Leg-spinning All-rounder",
        "teams": ["Sri Lanka", "Sunrisers Hyderabad"],
        "batting_career": {
            "Test": {"matches": 4, "innings": 7, "runs": 196, "highest": "59", "average": 28.00, "strike_rate": 81.66, "100s": 0, "50s": 1},
            "ODI": {"matches": 54, "innings": 45, "runs": 894, "highest": "80*", "average": 23.52, "strike_rate": 108.75, "100s": 0, "50s": 4},
            "T20I": {"matches": 68, "innings": 52, "runs": 652, "highest": "71", "average": 15.16, "strike_rate": 130.40, "100s": 0, "50s": 2}
        },
        "bowling_career": {
            "Test": {"wickets": 4, "best": "4/171", "average": 100.75, "economy": 3.73},
            "ODI": {"wickets": 84, "best": "7/19", "average": 25.86, "economy": 5.06},
            "T20I": {"wickets": 110, "best": "4/9", "average": 15.36, "economy": 6.78}
        }
    },
    # --- WOMEN'S INTERNATIONAL ---
    "Smriti Mandhana": {
        "gender": "Women's",
        "country": "India",
        "role": "Opening Batsman",
        "teams": ["India Women", "Royal Challengers Bengaluru Women"],
        "batting_career": {
            "Test": {"matches": 7, "innings": 12, "runs": 629, "highest": "149", "average": 57.18, "strike_rate": 59.84, "100s": 2, "50s": 3},
            "ODI": {"matches": 85, "innings": 85, "runs": 3585, "highest": "136", "average": 45.37, "strike_rate": 85.25, "100s": 7, "50s": 26},
            "T20I": {"matches": 136, "innings": 132, "runs": 3493, "highest": "87", "average": 28.86, "strike_rate": 122.56, "100s": 0, "50s": 26}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "T20I": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0}
        }
    },
    "Harmanpreet Kaur": {
        "gender": "Women's",
        "country": "India",
        "role": "Middle-order Batsman / Captain",
        "teams": ["India Women", "Mumbai Indians Women"],
        "batting_career": {
            "Test": {"matches": 6, "innings": 9, "runs": 231, "highest": "69", "average": 28.87, "strike_rate": 60.15, "100s": 0, "50s": 1},
            "ODI": {"matches": 133, "innings": 115, "runs": 3565, "highest": "171*", "average": 37.92, "strike_rate": 74.28, "100s": 6, "50s": 18},
            "T20I": {"matches": 169, "innings": 150, "runs": 3322, "highest": "103", "average": 27.68, "strike_rate": 120.93, "100s": 1, "50s": 12}
        },
        "bowling_career": {
            "Test": {"wickets": 11, "best": "5/44", "average": 14.81, "economy": 2.65},
            "ODI": {"wickets": 31, "best": "2/16", "average": 45.96, "economy": 5.09},
            "T20I": {"wickets": 32, "best": "4/23", "average": 26.59, "economy": 6.27}
        }
    },
    "Meg Lanning": {
        "gender": "Women's",
        "country": "Australia",
        "role": "Top-order Batsman",
        "teams": ["Australia Women", "Delhi Capitals Women"],
        "batting_career": {
            "Test": {"matches": 6, "innings": 12, "runs": 345, "highest": "93", "average": 31.36, "strike_rate": 53.65, "100s": 0, "50s": 2},
            "ODI": {"matches": 103, "innings": 102, "runs": 4602, "highest": "152*", "average": 53.51, "strike_rate": 92.20, "100s": 15, "50s": 21},
            "T20I": {"matches": 132, "innings": 121, "runs": 3405, "highest": "133*", "average": 36.61, "strike_rate": 116.37, "100s": 2, "50s": 15}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 10, "best": "2/39", "average": 17.00, "economy": 4.14},
            "T20I": {"wickets": 4, "best": "2/18", "average": 18.00, "economy": 6.00}
        }
    },
    "Ellyse Perry": {
        "gender": "Women's",
        "country": "Australia",
        "role": "All-rounder",
        "teams": ["Australia Women", "Royal Challengers Bengaluru Women"],
        "batting_career": {
            "Test": {"matches": 13, "innings": 23, "runs": 925, "highest": "213*", "average": 61.66, "strike_rate": 42.06, "100s": 2, "50s": 4},
            "ODI": {"matches": 144, "innings": 118, "runs": 3852, "highest": "112*", "average": 51.36, "strike_rate": 78.43, "100s": 3, "50s": 34},
            "T20I": {"matches": 154, "innings": 95, "runs": 1841, "highest": "75", "average": 31.20, "strike_rate": 115.42, "100s": 0, "50s": 9}
        },
        "bowling_career": {
            "Test": {"wickets": 39, "best": "7/22", "average": 21.64, "economy": 2.21},
            "ODI": {"wickets": 162, "best": "7/22", "average": 25.14, "economy": 4.36},
            "T20I": {"wickets": 126, "best": "4/12", "average": 18.96, "economy": 5.86}
        }
    },
    "Nat Sciver-Brunt": {
        "gender": "Women's",
        "country": "England",
        "role": "All-rounder",
        "teams": ["England Women", "Mumbai Indians Women"],
        "batting_career": {
            "Test": {"matches": 10, "innings": 18, "runs": 634, "highest": "169*", "average": 45.28, "strike_rate": 53.63, "100s": 1, "50s": 3},
            "ODI": {"matches": 100, "innings": 92, "runs": 3404, "highest": "148*", "average": 45.38, "strike_rate": 93.38, "100s": 8, "50s": 20},
            "T20I": {"matches": 116, "innings": 111, "runs": 2383, "highest": "82", "average": 26.77, "strike_rate": 116.18, "100s": 0, "50s": 13}
        },
        "bowling_career": {
            "Test": {"wickets": 11, "best": "3/41", "average": 35.81, "economy": 2.76},
            "ODI": {"wickets": 74, "best": "4/59", "average": 30.67, "economy": 4.54},
            "T20I": {"wickets": 86, "best": "4/15", "average": 21.55, "economy": 6.55}
        }
    },
    "Chamari Athapaththu": {
        "gender": "Women's",
        "country": "Sri Lanka",
        "role": "Opening Batsman / All-rounder",
        "teams": ["Sri Lanka Women", "UP Warriorz"],
        "batting_career": {
            "Test": {"matches": 0, "innings": 0, "runs": 0, "highest": "0", "average": 0.0, "strike_rate": 0.0, "100s": 0, "50s": 0},
            "ODI": {"matches": 103, "innings": 102, "runs": 3513, "highest": "195*", "average": 36.59, "strike_rate": 78.43, "100s": 9, "50s": 16},
            "T20I": {"matches": 139, "innings": 137, "runs": 3326, "highest": "119*", "average": 25.38, "strike_rate": 107.50, "100s": 3, "50s": 10}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 31, "best": "4/30", "average": 41.54, "economy": 5.37},
            "T20I": {"wickets": 49, "best": "3/17", "average": 28.71, "economy": 6.64}
        }
    },
    "Sophie Ecclestone": {
        "gender": "Women's",
        "country": "England",
        "role": "Slow Left-arm Orthodox Bowler",
        "teams": ["England Women", "UP Warriorz"],
        "batting_career": {
            "Test": {"matches": 7, "innings": 12, "runs": 169, "highest": "35", "average": 15.36, "strike_rate": 45.18, "100s": 0, "50s": 0},
            "ODI": {"matches": 63, "innings": 35, "runs": 322, "highest": "33*", "average": 15.33, "strike_rate": 76.84, "100s": 0, "50s": 0},
            "T20I": {"matches": 84, "innings": 32, "runs": 194, "highest": "33*", "average": 13.85, "strike_rate": 106.01, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 27, "best": "5/63", "average": 34.33, "economy": 2.76},
            "ODI": {"wickets": 98, "best": "6/36", "average": 21.41, "economy": 3.75},
            "T20I": {"wickets": 121, "best": "4/9", "average": 14.88, "economy": 5.82}
        }
    },
    "Deepti Sharma": {
        "gender": "Women's",
        "country": "India",
        "role": "All-rounder",
        "teams": ["India Women", "UP Warriorz"],
        "batting_career": {
            "Test": {"matches": 4, "innings": 7, "runs": 274, "highest": "78", "average": 45.66, "strike_rate": 51.31, "100s": 0, "50s": 3},
            "ODI": {"matches": 92, "innings": 75, "runs": 2049, "highest": "188", "average": 35.32, "strike_rate": 66.80, "100s": 1, "50s": 12},
            "T20I": {"matches": 117, "innings": 82, "runs": 1020, "highest": "64", "average": 24.87, "strike_rate": 106.36, "100s": 0, "50s": 2}
        },
        "bowling_career": {
            "Test": {"wickets": 16, "best": "5/7", "average": 14.43, "economy": 2.51},
            "ODI": {"wickets": 106, "best": "6/20", "average": 30.12, "economy": 4.22},
            "T20I": {"wickets": 131, "best": "4/10", "average": 19.07, "economy": 6.10}
        }
    },
    "Hardik Pandya": {
        "gender": "Men's",
        "country": "India",
        "role": "Fast-bowling All-rounder",
        "teams": ["India", "Mumbai Indians"],
        "batting_career": {
            "Test": {"matches": 11, "innings": 18, "runs": 532, "highest": "108", "average": 31.29, "strike_rate": 73.88, "100s": 1, "50s": 4},
            "ODI": {"matches": 86, "innings": 61, "runs": 1769, "highest": "92*", "average": 34.01, "strike_rate": 110.35, "100s": 0, "50s": 11},
            "T20I": {"matches": 104, "innings": 79, "runs": 1641, "highest": "71*", "average": 27.81, "strike_rate": 141.22, "100s": 0, "50s": 4}
        },
        "bowling_career": {
            "Test": {"wickets": 17, "best": "5/28", "average": 31.05, "economy": 3.38},
            "ODI": {"wickets": 84, "best": "4/24", "average": 35.60, "economy": 5.56},
            "T20I": {"wickets": 86, "best": "4/16", "average": 25.43, "economy": 8.08}
        }
    },
    "Mitchell Starc": {
        "gender": "Men's",
        "country": "Australia",
        "role": "Fast Bowler",
        "teams": ["Australia", "Kolkata Knight Riders", "New South Wales"],
        "batting_career": {
            "Test": {"matches": 89, "innings": 133, "runs": 2096, "highest": "99", "average": 20.35, "strike_rate": 66.88, "100s": 0, "50s": 10},
            "ODI": {"matches": 121, "innings": 69, "runs": 551, "highest": "52*", "average": 12.81, "strike_rate": 79.51, "100s": 0, "50s": 1},
            "T20I": {"matches": 65, "innings": 17, "runs": 94, "highest": "14", "average": 9.40, "strike_rate": 93.07, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 358, "best": "6/50", "average": 27.74, "economy": 3.42},
            "ODI": {"wickets": 236, "best": "6/28", "average": 22.96, "economy": 5.15},
            "T20I": {"wickets": 79, "best": "4/20", "average": 23.81, "economy": 7.64}
        }
    },
    "Ben Stokes": {
        "gender": "Men's",
        "country": "England",
        "role": "All-rounder / Test Captain",
        "teams": ["England", "Durham"],
        "batting_career": {
            "Test": {"matches": 105, "innings": 191, "runs": 6508, "highest": "258", "average": 35.75, "strike_rate": 59.34, "100s": 13, "50s": 34},
            "ODI": {"matches": 114, "innings": 99, "runs": 3159, "highest": "182", "average": 38.99, "strike_rate": 96.33, "100s": 5, "50s": 22},
            "T20I": {"matches": 43, "innings": 36, "runs": 585, "highest": "52*", "average": 21.66, "strike_rate": 128.00, "100s": 0, "50s": 1}
        },
        "bowling_career": {
            "Test": {"wickets": 203, "best": "6/22", "average": 32.07, "economy": 3.31},
            "ODI": {"wickets": 74, "best": "5/61", "average": 42.39, "economy": 6.05},
            "T20I": {"wickets": 26, "best": "3/26", "average": 32.92, "economy": 8.46}
        }
    },
    "Shaheen Shah Afridi": {
        "gender": "Men's",
        "country": "Pakistan",
        "role": "Fast Bowler",
        "teams": ["Pakistan", "Lahore Qalandars"],
        "batting_career": {
            "Test": {"matches": 30, "innings": 48, "runs": 393, "highest": "51*", "average": 12.67, "strike_rate": 45.00, "100s": 0, "50s": 1},
            "ODI": {"matches": 53, "innings": 24, "runs": 165, "highest": "25", "average": 10.31, "strike_rate": 78.57, "100s": 0, "50s": 0},
            "T20I": {"matches": 70, "innings": 22, "runs": 104, "highest": "23*", "average": 11.55, "strike_rate": 126.82, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 115, "best": "6/51", "average": 27.08, "economy": 3.14},
            "ODI": {"wickets": 104, "best": "6/35", "average": 23.94, "economy": 5.51},
            "T20I": {"wickets": 96, "best": "4/22", "average": 20.82, "economy": 7.74}
        }
    },
    "Trent Boult": {
        "gender": "Men's",
        "country": "New Zealand",
        "role": "Fast Bowler",
        "teams": ["New Zealand", "Rajasthan Royals"],
        "batting_career": {
            "Test": {"matches": 78, "innings": 106, "runs": 759, "highest": "52*", "average": 15.81, "strike_rate": 62.98, "100s": 0, "50s": 1},
            "ODI": {"matches": 114, "innings": 44, "runs": 196, "highest": "21*", "average": 9.33, "strike_rate": 68.77, "100s": 0, "50s": 0},
            "T20I": {"matches": 61, "innings": 12, "runs": 38, "highest": "16", "average": 6.33, "strike_rate": 67.85, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 317, "best": "6/30", "average": 27.49, "economy": 2.98},
            "ODI": {"wickets": 211, "best": "7/34", "average": 23.97, "economy": 4.93},
            "T20I": {"wickets": 83, "best": "4/13", "average": 21.43, "economy": 7.68}
        }
    },
    "Shakib Al Hasan": {
        "gender": "Men's",
        "country": "Bangladesh",
        "role": "All-rounder",
        "teams": ["Bangladesh", "Kolkata Knight Riders"],
        "batting_career": {
            "Test": {"matches": 71, "innings": 130, "runs": 4609, "highest": "217", "average": 37.77, "strike_rate": 61.84, "100s": 5, "50s": 31},
            "ODI": {"matches": 247, "innings": 234, "runs": 7570, "highest": "134*", "average": 37.29, "strike_rate": 82.85, "100s": 9, "50s": 56},
            "T20I": {"matches": 129, "innings": 127, "runs": 2551, "highest": "84*", "average": 23.19, "strike_rate": 121.18, "100s": 0, "50s": 13}
        },
        "bowling_career": {
            "Test": {"wickets": 246, "best": "7/36", "average": 31.72, "economy": 3.01},
            "ODI": {"wickets": 317, "best": "5/29", "average": 29.52, "economy": 4.45},
            "T20I": {"wickets": 149, "best": "5/20", "average": 20.45, "economy": 6.78}
        }
    },
    "Alyssa Healy": {
        "gender": "Women's",
        "country": "Australia",
        "role": "Wicketkeeper-Batsman / Captain",
        "teams": ["Australia Women", "UP Warriorz", "Sydney Sixers Women"],
        "batting_career": {
            "Test": {"matches": 9, "innings": 17, "runs": 445, "highest": "99", "average": 26.17, "strike_rate": 53.61, "100s": 0, "50s": 3},
            "ODI": {"matches": 110, "innings": 99, "runs": 3011, "highest": "170", "average": 34.60, "strike_rate": 99.80, "100s": 5, "50s": 16},
            "T20I": {"matches": 162, "innings": 143, "runs": 3054, "highest": "148*", "average": 25.45, "strike_rate": 130.40, "100s": 1, "50s": 17}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "T20I": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0}
        }
    },
    "Beth Mooney": {
        "gender": "Women's",
        "country": "Australia",
        "role": "Top-order Batsman",
        "teams": ["Australia Women", "Gujarat Giants"],
        "batting_career": {
            "Test": {"matches": 7, "innings": 13, "runs": 442, "highest": "122", "average": 40.18, "strike_rate": 52.86, "100s": 1, "50s": 2},
            "ODI": {"matches": 74, "innings": 64, "runs": 2380, "highest": "133", "average": 52.88, "strike_rate": 87.72, "100s": 3, "50s": 16},
            "T20I": {"matches": 101, "innings": 94, "runs": 2947, "highest": "117*", "average": 40.93, "strike_rate": 124.60, "100s": 2, "50s": 22}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "T20I": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0}
        }
    },
    "Laura Wolvaardt": {
        "gender": "Women's",
        "country": "South Africa",
        "role": "Opening Batsman / Captain",
        "teams": ["South Africa Women", "Gujarat Giants"],
        "batting_career": {
            "Test": {"matches": 4, "innings": 8, "runs": 357, "highest": "122", "average": 51.00, "strike_rate": 48.97, "100s": 1, "50s": 2},
            "ODI": {"matches": 98, "innings": 97, "runs": 3973, "highest": "184*", "average": 48.45, "strike_rate": 72.88, "100s": 8, "50s": 32},
            "T20I": {"matches": 75, "innings": 70, "runs": 1850, "highest": "102", "average": 35.57, "strike_rate": 114.76, "100s": 1, "50s": 11}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "T20I": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0}
        }
    },
    "Marizanne Kapp": {
        "gender": "Women's",
        "country": "South Africa",
        "role": "Fast-bowling All-rounder",
        "teams": ["South Africa Women", "Delhi Capitals Women"],
        "batting_career": {
            "Test": {"matches": 4, "innings": 8, "runs": 274, "highest": "150", "average": 39.14, "strike_rate": 49.36, "100s": 1, "50s": 0},
            "ODI": {"matches": 141, "innings": 125, "runs": 2707, "highest": "102*", "average": 32.22, "strike_rate": 78.43, "100s": 2, "50s": 14},
            "T20I": {"matches": 106, "innings": 89, "runs": 1532, "highest": "75", "average": 21.57, "strike_rate": 102.61, "100s": 0, "50s": 4}
        },
        "bowling_career": {
            "Test": {"wickets": 7, "best": "5/58", "average": 38.85, "economy": 2.88},
            "ODI": {"wickets": 153, "best": "5/45", "average": 27.53, "economy": 3.78},
            "T20I": {"wickets": 83, "best": "4/14", "average": 21.08, "economy": 5.56}
        }
    },
    "Amelia Kerr": {
        "gender": "Women's",
        "country": "New Zealand",
        "role": "Leg-spinning All-rounder",
        "teams": ["New Zealand Women", "Mumbai Indians Women"],
        "batting_career": {
            "Test": {"matches": 1, "innings": 2, "runs": 8, "highest": "6", "average": 4.00, "strike_rate": 20.51, "100s": 0, "50s": 0},
            "ODI": {"matches": 77, "innings": 69, "runs": 2056, "highest": "232*", "average": 39.53, "strike_rate": 83.74, "100s": 3, "50s": 9},
            "T20I": {"matches": 82, "innings": 69, "runs": 1340, "highest": "70*", "average": 26.27, "strike_rate": 108.76, "100s": 0, "50s": 2}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 90, "best": "5/17", "average": 30.64, "economy": 4.88},
            "T20I": {"wickets": 79, "best": "4/20", "average": 21.43, "economy": 5.92}
        }
    },
    "Hayley Matthews": {
        "gender": "Women's",
        "country": "West Indies",
        "role": "All-rounder / Captain",
        "teams": ["West Indies Women", "Mumbai Indians Women"],
        "batting_career": {
            "Test": {"matches": 0, "innings": 0, "runs": 0, "highest": "0", "average": 0.0, "strike_rate": 0.0, "100s": 0, "50s": 0},
            "ODI": {"matches": 90, "innings": 89, "runs": 2466, "highest": "140*", "average": 29.35, "strike_rate": 78.43, "100s": 5, "50s": 12},
            "T20I": {"matches": 96, "innings": 95, "runs": 2339, "highest": "132", "average": 26.57, "strike_rate": 113.81, "100s": 2, "50s": 13}
        },
        "bowling_career": {
            "Test": {"wickets": 0, "best": "0/0", "average": 0.0, "economy": 0.0},
            "ODI": {"wickets": 103, "best": "4/15", "average": 28.52, "economy": 4.29},
            "T20I": {"wickets": 99, "best": "4/15", "average": 18.25, "economy": 5.86}
        }
    },
    "Shafali Verma": {
        "gender": "Women's",
        "country": "India",
        "role": "Opening Batsman",
        "teams": ["India Women", "Delhi Capitals Women"],
        "batting_career": {
            "Test": {"matches": 5, "innings": 10, "runs": 567, "highest": "205", "average": 63.00, "strike_rate": 81.34, "100s": 1, "50s": 3},
            "ODI": {"matches": 26, "innings": 26, "runs": 589, "highest": "71*", "average": 23.56, "strike_rate": 83.42, "100s": 0, "50s": 4},
            "T20I": {"matches": 81, "innings": 80, "runs": 1948, "highest": "81", "average": 24.97, "strike_rate": 129.60, "100s": 0, "50s": 10}
        },
        "bowling_career": {
            "Test": {"wickets": 3, "best": "2/8", "average": 10.66, "economy": 2.46},
            "ODI": {"wickets": 1, "best": "1/5", "average": 44.00, "economy": 5.50},
            "T20I": {"wickets": 6, "best": "3/22", "average": 18.33, "economy": 7.02}
        }
    },
    "Renuka Singh Thakur": {
        "gender": "Women's",
        "country": "India",
        "role": "Fast Bowler",
        "teams": ["India Women", "Royal Challengers Bengaluru Women"],
        "batting_career": {
            "Test": {"matches": 2, "innings": 3, "runs": 3, "highest": "3", "average": 1.50, "strike_rate": 15.00, "100s": 0, "50s": 0},
            "ODI": {"matches": 13, "innings": 5, "runs": 10, "highest": "4", "average": 5.00, "strike_rate": 35.71, "100s": 0, "50s": 0},
            "T20I": {"matches": 47, "innings": 9, "runs": 18, "highest": "7", "average": 6.00, "strike_rate": 69.23, "100s": 0, "50s": 0}
        },
        "bowling_career": {
            "Test": {"wickets": 2, "best": "1/30", "average": 45.00, "economy": 2.72},
            "ODI": {"wickets": 22, "best": "4/28", "average": 22.04, "economy": 4.67},
            "T20I": {"wickets": 50, "best": "5/15", "average": 21.60, "economy": 6.44}
        }
    }
}

def get_player_stats(player_name):
    """Retrieve verified international player profile and career stats."""
    player = INTERNATIONAL_PLAYERS_DATA.get(player_name)
    if not player:
        return {"error": f"Player '{player_name}' not found in international roster."}
    return player

def get_filtered_players(gender="All", country="All", role="All", search_term=""):
    """Filter real international players by gender, country, role, and search term."""
    results = []
    for name, data in INTERNATIONAL_PLAYERS_DATA.items():
        if gender != "All" and data.get("gender") != gender:
            continue
        if country != "All" and data.get("country") != country:
            continue
        if role != "All" and role.lower() not in data.get("role", "").lower():
            continue
        if search_term and search_term.lower() not in name.lower() and search_term.lower() not in data.get("country", "").lower():
            continue
        results.append(name)
    return sorted(results)

def search_api_player(player_name):
    """Search Cricbuzz RapidAPI for live international player stats if API key is available.

    Returns:
        list[dict]  – player results on success
        {"quota_exceeded": True}  – when HTTP 429 is returned (quota exhausted)
        None  – on network error or missing key/name
    """
    api_key = get_rapidapi_key()
    if not api_key or not player_name:
        return None
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }
    try:
        resp = requests.get(url, headers=headers, params={"plrN": player_name}, timeout=10)
        if resp.status_code == 429:
            return {"quota_exceeded": True}
        if resp.status_code == 200:
            data = resp.json()
            return data.get("player", [])
    except Exception:
        pass
    return None

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏆",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

def navigate_page(page):
    st.session_state.page = page


@st.cache_resource(show_spinner="Loading ML model...")
def load_ml_model_bundle():
    return get_model_bundle()


def get_rapidapi_key():
    try:
        if "RAPIDAPI_KEY" in st.secrets:
            return st.secrets["RAPIDAPI_KEY"]
    except Exception:
        pass

    return os.getenv("RAPIDAPI_KEY", "")


def apply_chart_theme(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0)",
        plot_bgcolor="rgba(15, 23, 42, 0)",
        font=dict(color="#e2e8f0", size=12),
        legend=dict(
            font=dict(color="#f8fafc", size=12),
            bgcolor="rgba(15, 23, 42, 0.35)"
        ),
        height=height
    )
    fig.update_xaxes(
        color="#e2e8f0",
        gridcolor="rgba(148, 163, 184, 0.18)",
        linecolor="rgba(148, 163, 184, 0.30)",
        zerolinecolor="rgba(148, 163, 184, 0.25)"
    )
    fig.update_yaxes(
        color="#e2e8f0",
        gridcolor="rgba(148, 163, 184, 0.18)",
        linecolor="rgba(148, 163, 184, 0.30)",
        zerolinecolor="rgba(148, 163, 184, 0.25)"
    )
    fig.update_traces(
        selector=dict(type="pie"),
        textfont=dict(color="#f8fafc", size=12),
        textinfo="percent"
    )
    return fig

# ---------------- CRICKET API ABSTRACTION & CLASSIFICATION ----------------
import re

MAJOR_INTERNATIONAL_TEAMS = frozenset({
    "India", "Australia", "England", "South Africa", "New Zealand", "Pakistan",
    "Sri Lanka", "Bangladesh", "Afghanistan", "West Indies", "Zimbabwe",
    "Ireland", "Scotland", "Netherlands", "Namibia", "Nepal", "Oman",
    "United Arab Emirates", "UAE", "U.A.E.", "United States of America", "USA", "U.S.A.",
    "Papua New Guinea", "PNG", "Canada", "Kenya", "Uganda", "Italy",
    "Bermuda", "Jersey", "Guernsey", "Hong Kong", "Kuwait", "Bahrain",
    "Qatar", "Malaysia", "Singapore", "Tanzania", "Rwanda", "Nigeria",
    "Germany", "Denmark", "Japan", "Thailand", "Indonesia", "Vanuatu",
    "Fiji", "Samoa", "Argentina", "Brazil", "Botswana", "Sierra Leone"
})

TOP_TIER_TEAMS = frozenset({
    "India", "Australia", "England", "South Africa", "New Zealand",
    "Pakistan", "Sri Lanka", "Bangladesh", "Afghanistan", "West Indies"
})

FRANCHISE_KEYWORDS = [
    "IPL", "WPL", "BBL", "WBBL", "PSL", "CPL", "THE HUNDRED", "SUPER SMASH",
    "BIG BASH", "PREMIER LEAGUE", "T20 BLAST", "MAJOR LEAGUE", "SA20", "ILT20",
    "MLC", "GLOBAL T20", "LANKA PREMIER LEAGUE", "LPL", "BPL", "BANGLADESH PREMIER LEAGUE"
]

FRANCHISE_TEAMS = frozenset({
    "CSK", "MI", "RCB", "KKR", "RR", "DC", "GT", "LSG", "PBKS", "SRH",
    "Chennai Super Kings", "Mumbai Indians", "Royal Challengers Bengaluru",
    "Royal Challengers Bangalore", "Rajasthan Royals", "Delhi Capitals",
    "Delhi Daredevils", "Gujarat Titans", "Lucknow Super Giants", "Punjab Kings",
    "Kings XI Punjab", "Sunrisers Hyderabad", "Deccan Chargers", "Rising Pune Supergiant",
    "Gujarat Giants", "UP Warriorz", "Sydney Sixers", "Sydney Thunder",
    "Melbourne Stars", "Melbourne Renegades", "Perth Scorchers", "Brisbane Heat",
    "Hobart Hurricanes", "Adelaide Strikers", "Lahore Qalandars", "Karachi Kings",
    "Islamabad United", "Peshawar Zalmi", "Quetta Gladiators", "Multan Sultans",
    "Trinbago Knight Riders", "Guyana Amazon Warriors", "Barbados Royals",
    "St Kitts & Nevis Patriots", "Saint Lucia Kings", "Antigua & Barbuda Falcons",
    "Oval Invincibles", "Southern Brave", "Manchester Originals", "Trent Rockets",
    "Birmingham Phoenix", "Northern Superchargers", "London Spirit", "Welsh Fire",
    "MI Cape Town", "Paarl Royals", "Pretoria Capitals", "Sunrisers Eastern Cape",
    "Joburg Super Kings", "Durban's Super Giants"
})

# Strict non-senior and non-national team exclusion patterns
TEAM_REJECT_PATTERNS = [
    r"\b[A-C]\b",                          # A, B, C teams (e.g. India A, Australia A, India B)
    r"\bUnder[-\s]?\d+\b",                 # Under-19, Under-20, Under-23, etc.
    r"\bU[-\s]?\d+\b",                     # U19, U20, U23, etc.
    r"\bYouth\b", r"\bJunior\b", r"\bColts\b",  # Youth/Junior squads
    r"\bEmerging\b",                       # Emerging teams
    r"\bDevelopment\b", r"\bPathway\b",    # Development squads
    r"\bLions\b", r"\bShaheens\b", r"\bWolves\b",  # A-team brands
    r"\bXI\b", r"\bXI'?s\b",               # XI teams (Prime Minister's XI, Board President's XI)
    r"\bPresident'?s\b", r"\bGovernor'?s\b", r"\bChairman'?s\b", r"\bPrime Minister'?s\b", r"\bPM'?s\b",
    r"\bInvitational?\b", r"\bSelect\b", r"\bCombined\b", r"\bRest of\b",
    r"\bAcademy\b", r"\bAcademies\b",      # Academies
    r"\bClub\b", r"\bMCC\b",               # Clubs
    r"\bUniversity\b", r"\bUniversities\b", r"\bCollege\b", r"\bColleges\b", r"\bInstitute\b", r"\bSchool\b",
    r"\bCounty\b", r"\bRanji\b", r"\bDomestic\b",
    r"\bWarm[-\s]?up\b", r"\bPractice\b",
    r"\bSquad\b", r"\bReserves?\b"
]
TEAM_REJECT_REGEX = re.compile("|".join(TEAM_REJECT_PATTERNS), re.IGNORECASE)

# Series patterns that indicate youth, reserve, or unofficial cricket
SERIES_REJECT_PATTERNS = [
    r"\bUnder[-\s]?\d+\b",                 # U19/U20/youth tournaments
    r"\bU[-\s]?\d+\b",
    r"\bYouth\b", r"\bJunior\b", r"\bColts\b",
    r"\bEmerging\b",                       # Emerging Asia Cup, Emerging Nations
    r"\bDevelopment\b", r"\bPathway\b",
    r"\bLions\b", r"\bShaheens\b", r"\bWolves\b",
    # Specific A-team tours (e.g. "India A Tour", "Australia A in England")
    r"\b(?:India|Australia|England|South Africa|New Zealand|Pakistan|Sri Lanka|Bangladesh|Afghanistan|West Indies|Zimbabwe|Ireland|Scotland|Netherlands|Namibia|Nepal|Oman|USA|UAE)\s+A\b",
    r"\bA\s+(?:Tour|Team|Series)\b",
    r"\bUnofficial\b",                     # Unofficial Tests / ODIs
    r"\bPrime Minister'?s\b", r"\bBoard President\b", r"\bGovernor'?s\b", r"\bChairman'?s\b", r"\bInvitational?\b", r"\bSelect XI\b",
    r"\bAcademy\b", r"\bAcademies\b", r"\bClub\b", r"\bCollege\b", r"\bUniversity\b", r"\bInstitute\b", r"\bSchool\b",
    r"\bCounty\b", r"\bRanji\b", r"\bSheffield Shield\b", r"\bPlunket Shield\b", r"\bMarsh Cup\b", r"\bFord Trophy\b",
    r"\bQuaid[-\s]?e[-\s]?Azam\b", r"\bVitality Blast\b", r"\bCounty Championship\b", r"\bOne[-\s]?Day Cup\b",
    r"\bWarm[-\s]?up\b", r"\bPractice Match\b"
]
SERIES_REJECT_REGEX = re.compile("|".join(SERIES_REJECT_PATTERNS), re.IGNORECASE)

VALID_INTL_FORMATS = frozenset({"TEST", "ODI", "T20", "T20I"})

TEAM_FLAGS = {
    "India": "🇮🇳", "India Women": "🇮🇳",
    "Australia": "🇦🇺", "Australia Women": "🇦🇺",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "England Women": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "South Africa": "🇿🇦", "South Africa Women": "🇿🇦",
    "New Zealand": "🇳🇿", "New Zealand Women": "🇳🇿",
    "Pakistan": "🇵🇰", "Pakistan Women": "🇵🇰",
    "Sri Lanka": "🇱🇰", "Sri Lanka Women": "🇱🇰",
    "Bangladesh": "🇧🇩", "Bangladesh Women": "🇧🇩",
    "Afghanistan": "🇦🇫", "Afghanistan Women": "🇦🇫",
    "West Indies": "🌴", "West Indies Women": "🌴",
    "Zimbabwe": "🇿🇼", "Zimbabwe Women": "🇿🇼",
    "Ireland": "🇮🇪", "Ireland Women": "🇮🇪",
    "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Scotland Women": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Netherlands": "🇳🇱", "Netherlands Women": "🇳🇱",
    "Namibia": "🇳🇦", "Namibia Women": "🇳🇦",
    "Nepal": "🇳🇵", "Nepal Women": "🇳🇵",
    "Oman": "🇴🇲", "Oman Women": "🇴🇲",
    "UAE": "🇦🇪", "United Arab Emirates": "🇦🇪", "UAE Women": "🇦🇪",
    "USA": "🇺🇸", "United States of America": "🇺🇸", "United States": "🇺🇸", "USA Women": "🇺🇸",
    "Papua New Guinea": "🇵🇬", "PNG": "🇵🇬",
    "Canada": "🇨🇦", "Kenya": "🇰🇪", "Uganda": "🇺🇬", "Italy": "🇮🇹",
    "Hong Kong": "🇭🇰", "Hong Kong, China": "🇭🇰", "Kuwait": "🇰🇼", "Thailand": "🇹🇭", "Thailand Women": "🇹🇭"
}

def clean_team_name(name):
    if not name:
        return ""
    return str(name).strip()

def get_core_country(team_name):
    clean = clean_team_name(team_name)
    clean = re.sub(r"\b(Women's|Women|Woman|Wom|Men's|Men)\b", "", clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r"\s+W\b", "", clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r"^[\s\-–—]+|[\s\-–—]+$", "", clean).strip()
    return clean

def is_franchise_match(team1, team2, series_name=""):
    s_upper = (series_name or "").upper()
    t1 = clean_team_name(team1)
    t2 = clean_team_name(team2)

    for kw in FRANCHISE_KEYWORDS:
        if kw in s_upper or kw in t1.upper() or kw in t2.upper():
            return True

    for ft in FRANCHISE_TEAMS:
        if ft.lower() == t1.lower() or ft.lower() == t2.lower():
            return True
        if ft.lower() in t1.lower() or ft.lower() in t2.lower():
            return True

    return False

def is_international_match(team1, team2, series_name="", match_format=""):
    """Strictly validate whether a match is official senior national team cricket.

    Includes:
        - Senior men's & women's national teams (India, Australia, England, etc.)
        - Tests, ODIs, T20Is
        - Official bilateral series and ICC tournaments

    Excludes:
        - A-teams, B-teams, Lions, Shaheens, Wolves
        - Emerging teams & development squads
        - U19, U20, U23, youth, junior & colts teams
        - XI teams (Prime Minister's XI, Board President's XI, Select XI)
        - County, domestic, club, academy & university teams
        - Franchise leagues (IPL, WPL, BBL, PSL, etc.)
        - Warm-up & practice matches
        - Unconfirmed / non-senior classifications
    """
    t1 = clean_team_name(team1)
    t2 = clean_team_name(team2)
    s = series_name or ""

    # 1. Reject if franchise league match
    if is_franchise_match(team1, team2, series_name):
        return False

    # 2. Reject if match format is explicitly provided and not senior international (Test, ODI, T20/T20I)
    if match_format:
        fmt_clean = str(match_format).strip().upper()
        if fmt_clean not in VALID_INTL_FORMATS:
            return False

    # 3. Reject if team names contain non-senior or non-national indicators
    if TEAM_REJECT_REGEX.search(t1) or TEAM_REJECT_REGEX.search(t2):
        return False

    # 4. Reject if series name indicates non-senior cricket (U19, Emerging, Lions, A-tours, warm-ups, etc.)
    # Note: No bypass — senior ICC tournaments (World Cup, Champions Trophy, Ashes, BGT)
    # do NOT contain any of the reject patterns.
    if SERIES_REJECT_REGEX.search(s):
        return False

    c1 = get_core_country(t1)
    c2 = get_core_country(t2)

    # 5. Reject intra-squad / practice fixtures where both sides resolve to the same nation
    if c1.lower() == c2.lower():
        return False

    # 6. Both teams must be confidently recognized senior national teams
    is_c1_intl = any(c1.lower() == m.lower() for m in MAJOR_INTERNATIONAL_TEAMS)
    is_c2_intl = any(c2.lower() == m.lower() for m in MAJOR_INTERNATIONAL_TEAMS)

    return is_c1_intl and is_c2_intl


def detect_gender(team1, team2, series_name=""):
    combined = f"{team1} {team2} {series_name}".lower()
    if re.search(r"\b(women|women's|woman|wodi|wt20i|wtest)\b", combined) or " w " in f" {combined} ":
        return "Women's"
    return "Men's"

def get_match_priority(team1, team2):
    c1 = get_core_country(team1).lower()
    c2 = get_core_country(team2).lower()
    if c1 == "india" or c2 == "india":
        return 1
    is_top1 = any(c1 == t.lower() for t in TOP_TIER_TEAMS)
    is_top2 = any(c2 == t.lower() for t in TOP_TIER_TEAMS)
    if is_top1 or is_top2:
        return 2
    return 3

def get_team_flag(team_name):
    clean = clean_team_name(team_name)
    if clean in TEAM_FLAGS:
        return TEAM_FLAGS[clean]
    core = get_core_country(clean)
    if core in TEAM_FLAGS:
        return TEAM_FLAGS[core]
    for key, flag in TEAM_FLAGS.items():
        if key.lower() == clean.lower() or key.lower() == core.lower():
            return flag
    return "🏏"

def format_score_str(inngs):
    if not inngs or not isinstance(inngs, dict):
        return ""
    runs = inngs.get("runs")
    wkts = inngs.get("wickets")
    overs = inngs.get("overs")
    if runs is None:
        return ""
    wkt_str = f"/{wkts}" if wkts is not None else ""
    over_str = f" ({overs} ov)" if overs is not None else ""
    return f"{runs}{wkt_str}{over_str}"

def fetch_api_matches(endpoint="live"):
    """Fetch live, upcoming, or recent matches from Cricbuzz RapidAPI if key is available."""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/matches/v1/{endpoint}"
    api_key = get_rapidapi_key()

    if not api_key:
        return []

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        data = response.json()
        matches = []

        for type_match in data.get("typeMatches", []):
            match_type_cat = type_match.get("matchType", "")
            for series in type_match.get("seriesMatches", []):
                ad_wrapper = series.get("seriesAdWrapper", {})
                series_name = ad_wrapper.get("seriesName", "")

                for match in ad_wrapper.get("matches", []):
                    info = match.get("matchInfo", {})
                    score = match.get("matchScore", {})

                    team1 = info.get("team1", {}).get("teamName", "")
                    team2 = info.get("team2", {}).get("teamName", "")
                    status = info.get("status", "")
                    state = info.get("state", "").lower()
                    match_format = info.get("matchFormat", "T20I")
                    venue_info = info.get("venueInfo", {})
                    venue = venue_info.get("ground", "")
                    city = venue_info.get("city", "")
                    start_date = info.get("startDate", "")

                    t1_inngs1 = score.get("team1Score", {}).get("inngs1", {})
                    t2_inngs1 = score.get("team2Score", {}).get("inngs1", {})
                    t1_inngs2 = score.get("team1Score", {}).get("inngs2", {})
                    t2_inngs2 = score.get("team2Score", {}).get("inngs2", {})

                    t1_score_str = format_score_str(t1_inngs1)
                    if t1_inngs2:
                        t1_score_str += f" & {format_score_str(t1_inngs2)}"

                    t2_score_str = format_score_str(t2_inngs1)
                    if t2_inngs2:
                        t2_score_str += f" & {format_score_str(t2_inngs2)}"

                    gender = detect_gender(team1, team2, series_name)
                    # Strict validation: never allow club, academy, A-teams into international
                    is_intl = is_international_match(team1, team2, series_name, match_format)
                    is_fran = is_franchise_match(team1, team2, series_name)
                    priority = get_match_priority(team1, team2)

                    if "in progress" in state or "live" in state or "stumps" in status.lower() or "tea" in status.lower() or "lunch" in status.lower():
                        stage = "Live"
                    elif "complete" in state or "result" in state:
                        stage = "Completed"
                    else:
                        stage = "Upcoming"

                    matches.append({
                        "team1": team1,
                        "team2": team2,
                        "team1_flag": get_team_flag(team1),
                        "team2_flag": get_team_flag(team2),
                        "status": status,
                        "score1": t1_score_str,
                        "score2": t2_score_str,
                        "t1runs": t1_inngs1.get("runs"),
                        "t1wkts": t1_inngs1.get("wickets"),
                        "t2runs": t2_inngs1.get("runs"),
                        "t2wkts": t2_inngs1.get("wickets"),
                        "format": match_format,
                        "gender": gender,
                        "is_international": is_intl,
                        "is_franchise": is_fran,
                        "priority": priority,
                        "series": series_name,
                        "venue": f"{venue}, {city}".strip(", "),
                        "date": start_date,
                        "stage": stage,
                        "source": "Live Cricbuzz API"
                    })

        return matches
    except (requests.RequestException, ValueError):
        # Re-raise so fetch_api_matches_with_status can detect the failure and
        # correctly report api_available=False (covers 429, network errors, etc.)
        raise

def get_real_db_international_matches(limit=40, gender_filter=None):
    """Retrieve verified real international matches from cricket.db ml_international_matches."""
    try:
        conn = sqlite3.connect("cricket.db")
        cursor = conn.cursor()
        query = """
            SELECT team1, team2, format, gender, winner, team1_runs, team1_wickets,
                   team2_runs, team2_wickets, status, venue, match_date
            FROM ml_international_matches
        """
        params = []
        if gender_filter:
            target = "women" if "women" in gender_filter.lower() else "men"
            query += " WHERE gender = ?"
            params.append(target)

        query += " ORDER BY match_date DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        matches = []
        for r in rows:
            t1, t2, fmt, g, winner, r1, w1, r2, w2, st, venue, dt = r
            gen_label = "Women's" if g == "women" else "Men's"
            t1_display = f"{t1} Women" if g == "women" and not t1.endswith("Women") else t1
            t2_display = f"{t2} Women" if g == "women" and not t2.endswith("Women") else t2

            score1 = f"{r1}/{w1}" if r1 is not None else ""
            score2 = f"{r2}/{w2}" if r2 is not None else ""

            status_desc = f"{winner} won by match conclusion" if winner else "Match completed"
            if winner and r1 is not None and r2 is not None:
                if winner.lower() in t1.lower() and r1 > r2:
                    diff = r1 - r2
                    status_desc = f"{t1} won by {diff} runs"
                elif winner.lower() in t2.lower() and w2 is not None:
                    status_desc = f"{t2} won by {10 - w2} wickets"
                else:
                    status_desc = f"{winner} won"

            priority = get_match_priority(t1, t2)

            matches.append({
                "team1": t1_display,
                "team2": t2_display,
                "team1_flag": get_team_flag(t1),
                "team2_flag": get_team_flag(t2),
                "status": status_desc,
                "score1": score1,
                "score2": score2,
                "t1runs": r1, "t1wkts": w1,
                "t2runs": r2, "t2wkts": w2,
                "format": fmt,
                "gender": gen_label,
                "is_international": True,
                "is_franchise": False,
                "priority": priority,
                "series": f"ICC {fmt} Championship ({gen_label})",
                "venue": venue or "International Cricket Ground",
                "date": dt or "Recent",
                "stage": "Completed",
                "source": "ICC Real International Dataset"
            })

        return matches
    except Exception:
        return []

def get_real_franchise_matches():
    """Curated real franchise matches (IPL, WPL, BBL, PSL) kept strictly separate from international."""
    return [
        {
            "team1": "Royal Challengers Bengaluru",
            "team2": "Chennai Super Kings",
            "team1_flag": "🔴", "team2_flag": "🟡",
            "status": "RCB won by 27 runs - Qualified for Playoffs",
            "score1": "218/5 (20.0 ov)",
            "score2": "191/7 (20.0 ov)",
            "format": "T20", "gender": "Men's",
            "is_international": False, "is_franchise": True, "priority": 1,
            "series": "Indian Premier League (IPL)",
            "venue": "M. Chinnaswamy Stadium, Bengaluru",
            "date": "2026-05-18", "stage": "Completed",
            "source": "IPL Official Coverage"
        },
        {
            "team1": "Royal Challengers Bengaluru Women",
            "team2": "Delhi Capitals Women",
            "team1_flag": "🔴", "team2_flag": "🔵",
            "status": "RCB Women won by 8 wickets - WPL Champions",
            "score1": "115/2 (19.3 ov)",
            "score2": "113/10 (18.3 ov)",
            "format": "T20", "gender": "Women's",
            "is_international": False, "is_franchise": True, "priority": 1,
            "series": "Women's Premier League (WPL)",
            "venue": "Arun Jaitley Stadium, New Delhi",
            "date": "2026-03-17", "stage": "Completed",
            "source": "WPL Official Coverage"
        },
        {
            "team1": "Mumbai Indians",
            "team2": "Kolkata Knight Riders",
            "team1_flag": "🔵", "team2_flag": "🟣",
            "status": "KKR won by 24 runs",
            "score1": "145/10 (18.5 ov)",
            "score2": "169/10 (19.5 ov)",
            "format": "T20", "gender": "Men's",
            "is_international": False, "is_franchise": True, "priority": 2,
            "series": "Indian Premier League (IPL)",
            "venue": "Wankhede Stadium, Mumbai",
            "date": "2026-05-03", "stage": "Completed",
            "source": "IPL Official Coverage"
        },
        {
            "team1": "Mumbai Indians Women",
            "team2": "UP Warriorz",
            "team1_flag": "🔵", "team2_flag": "🟡",
            "status": "MI Women won by 42 runs",
            "score1": "160/6 (20.0 ov)",
            "score2": "118/9 (20.0 ov)",
            "format": "T20", "gender": "Women's",
            "is_international": False, "is_franchise": True, "priority": 2,
            "series": "Women's Premier League (WPL)",
            "venue": "M. Chinnaswamy Stadium, Bengaluru",
            "date": "2026-02-28", "stage": "Completed",
            "source": "WPL Official Coverage"
        },
        {
            "team1": "Sydney Sixers",
            "team2": "Perth Scorchers",
            "team1_flag": "💗", "team2_flag": "🟠",
            "status": "Sixers won by 3 wickets (DLS Method)",
            "score1": "152/7 (18.4 ov)",
            "score2": "149/9 (20.0 ov)",
            "format": "T20", "gender": "Men's",
            "is_international": False, "is_franchise": True, "priority": 3,
            "series": "Big Bash League (BBL)",
            "venue": "Sydney Cricket Ground, Sydney",
            "date": "2026-01-16", "stage": "Completed",
            "source": "BBL Official Coverage"
        },
        {
            "team1": "Lahore Qalandars",
            "team2": "Karachi Kings",
            "team1_flag": "🟢", "team2_flag": "🔵",
            "status": "Karachi Kings won by 3 wickets",
            "score1": "177/5 (20.0 ov)",
            "score2": "178/7 (19.4 ov)",
            "format": "T20", "gender": "Men's",
            "is_international": False, "is_franchise": True, "priority": 3,
            "series": "Pakistan Super League (PSL)",
            "venue": "Gaddafi Stadium, Lahore",
            "date": "2026-02-24", "stage": "Completed",
            "source": "PSL Official Coverage"
        }
    ]


# ---------------------------------------------------------------------------
# REMOVED: get_live_featured_international_matches() and
#          get_upcoming_international_fixtures()
#
# These functions contained hardcoded stale match data (including the
# India vs Australia Border-Gavaskar 4th Test marked as "stage: Live").
# They were NEVER called by the live pipeline but posed a data-integrity
# risk if accidentally wired in. Replaced with safety stubs below.
# LIVE and UPCOMING data MUST come exclusively from fetch_api_matches_with_status().
# Historical/Cricsheet data is ONLY permitted for Completed/Recent matches.
# ---------------------------------------------------------------------------

def get_live_featured_international_matches():
    """REMOVED — do not use. Raised to prevent accidental re-introduction of
    stale hardcoded LIVE data. Use get_live_matches() / get_matches('live') instead."""
    raise RuntimeError(
        "get_live_featured_international_matches() has been permanently disabled. "
        "LIVE matches must only come from the verified live API endpoint."
    )


def get_upcoming_international_fixtures():
    """REMOVED — do not use. Raised to prevent accidental re-introduction of
    stale hardcoded UPCOMING data. Use get_upcoming_matches() / get_matches('upcoming') instead."""
    raise RuntimeError(
        "get_upcoming_international_fixtures() has been permanently disabled. "
        "UPCOMING matches must only come from the verified live API endpoint."
    )


def fetch_api_matches_with_status(endpoint="live"):
    """
    Wrapper around fetch_api_matches that also returns whether the API responded.
    Returns (matches_list, api_was_available).

    api_was_available=False means: no key configured, quota exceeded (HTTP 429),
    network failure, or any other error — caller must NOT fall back to historical
    data for LIVE/UPCOMING; instead show 'data unavailable' message.

    api_was_available=True means: API returned a valid response (possibly 0 matches —
    that is a legitimate empty state, not a failure).
    """
    api_key = get_rapidapi_key()
    if not api_key:
        return [], False
    try:
        results = fetch_api_matches(endpoint)
        # Clean API response — 0 matches is a valid empty state (api_available=True)
        return results, True
    except Exception:
        # Any error (429 quota, timeout, parse failure) → treat API as unavailable
        return [], False


def get_matches(endpoint="live"):
    """
    International match retrieval.
    - live / upcoming: ONLY from the live API. Historical fallback data is NEVER
      substituted here, because showing stale fixtures as LIVE or UPCOMING is
      misleading. Returns (matches, api_available).
    - recent (completed): Falls back to the historical DB — those are genuinely
      historical results, not current state, so the fallback is appropriate.
    Franchise matches are always kept separate.
    """
    matches, api_available = fetch_api_matches_with_status(endpoint)
    intl_api = [m for m in matches if m.get("is_international")]

    if endpoint in ("live", "upcoming"):
        # Strict: never substitute historical data as current live/upcoming
        if intl_api:
            return sorted(intl_api,
                          key=lambda x: (x.get("priority", 3),
                                         0 if x.get("stage") == "Live" else 1)), True
        # API had a key but returned no matches → valid empty state (no matches on right now)
        # OR API key missing / error → unavailable
        return [], api_available

    else:  # endpoint == "recent" / completed
        if intl_api:
            return sorted(intl_api,
                          key=lambda x: (x.get("priority", 3), x.get("date", ""))), True
        # Fallback to historical DB for completed results is acceptable
        recent = get_real_db_international_matches(limit=40)
        return sorted(recent,
                      key=lambda x: (x.get("priority", 3), x.get("date", "")),
                      reverse=False), True


def get_live_matches():
    """Returns (matches, api_available). Matches is [] when API unavailable."""
    return get_matches("live")


def get_upcoming_matches():
    """Returns (matches, api_available). Matches is [] when API unavailable."""
    return get_matches("upcoming")


def get_completed_matches():
    """Returns (matches, api_available). Always returns results (DB fallback ok)."""
    return get_matches("recent")


def get_franchise_matches():
    """Retrieve franchise matches (IPL, WPL, BBL, PSL) from API or curated historical fixtures.
    Historical franchise data is fine here — they are clearly marked 'Completed'."""
    api_results = fetch_api_matches("live") + fetch_api_matches("recent")
    fran_api = [m for m in api_results if m.get("is_franchise")]
    if fran_api:
        return fran_api
    return get_real_franchise_matches()


def get_all_international_matches():
    """Returns (matches, live_api_available, upcoming_api_available)."""
    live_matches, live_api_ok = get_live_matches()
    upcoming_matches, upcoming_api_ok = get_upcoming_matches()
    completed_matches, _ = get_completed_matches()
    all_intl = live_matches + upcoming_matches + completed_matches
    seen = set()
    unique = []
    for m in all_intl:
        key = (m.get("team1", ""), m.get("team2", ""), m.get("format", ""), m.get("stage", ""))
        if key not in seen:
            seen.add(key)
            unique.append(m)
    sorted_matches = sorted(
        unique,
        key=lambda x: (x.get("priority", 3),
                       0 if x.get("stage") == "Live" else (1 if x.get("stage") == "Upcoming" else 2))
    )
    return sorted_matches, live_api_ok, upcoming_api_ok


# ---------------- DATABASE ----------------
def get_db_matches():
    conn = sqlite3.connect("cricket.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT team1, score, status
        FROM matches
        ORDER BY id DESC
        LIMIT 10
    """)

    data = cursor.fetchall()
    conn.close()
    return data

# ---------------- CSS ----------------
st.markdown("""
<style>

header {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1a1f3a 50%, #0f172a 100%);
    color: white;
}

/* Padding fix */
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Titles */
.title {
    font-size: 52px;
    font-weight: 900;
    background: linear-gradient(135deg, #38bdf8 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
    text-shadow: 0 2px 10px rgba(56, 189, 248, 0.2);
}

.subtitle {
    font-size: 18px;
    color: #a0aec0;
    margin-bottom: 30px;
    font-weight: 500;
}

/* Cards */
.card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.6) 100%);
    padding: 25px;
    border-radius: 16px;
    border: 2px solid rgba(56, 189, 248, 0.2);
    text-align: center;
    margin-bottom: 16px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card:hover {
    background: linear-gradient(135deg, rgba(51, 65, 85, 1) 0%, rgba(71, 85, 105, 0.9) 100%);
    border: 2px solid rgba(56, 189, 248, 0.5);
    box-shadow: 0 12px 40px rgba(56, 189, 248, 0.2);
    transform: translateY(-5px);
}

.card b {
    background: linear-gradient(135deg, #38bdf8 0%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 18px;
}

.card-icon {
    font-size: 32px;
    margin-bottom: 10px;
}

.card p {
    color: #cbd5e1;
    margin: 8px 0 0 0;
    font-size: 14px;
    line-height: 1.5;
}

/* Buttons FIXED */
.stButton {
    margin: 12px 0 !important;
    display: block !important;
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
    color: white;
    border: none;
    padding: 16px 20px !important;
    font-weight: 700;
    font-size: 15px;
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.3);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #38bdf8 0%, #22d3ee 100%);
    box-shadow: 0 8px 30px rgba(56, 189, 248, 0.4);
    transform: translateY(-2px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Dropdown FIX */
div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 8px !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
}

div[data-baseweb="select"] > div:hover {
    border: 1px solid rgba(56, 189, 248, 0.6) !important;
}

/* Text Input Styling */
input, textarea {
    background-color: rgba(30, 41, 59, 0.9) !important;
    color: #e0e7ff !important;
    border: 2px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    font-size: 15px !important;
}

input::placeholder, textarea::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}

input:focus, textarea:focus {
    background-color: rgba(30, 41, 59, 1) !important;
    border: 2px solid rgba(56, 189, 248, 0.8) !important;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    outline: none !important;
}

/* Labels and Text */
label, .stLabel {
    color: #e0e7ff !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}

/* Subheader and Text Elements */
h1, h2, h3, h4, h5, h6 {
    color: #f1f5f9 !important;
}

/* Main text */
p, span, div {
    color: #e2e8f0 !important;
}

/* Info/Success/Warning Styling */
.stInfo, [data-testid="stAlert"] {
    background-color: rgba(56, 189, 248, 0.15) !important;
    color: #38bdf8 !important;
    border-left: 4px solid #38bdf8 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

.stInfo p, [data-testid="stAlert"] p {
    color: #e0f2fe !important;
}

.stSuccess {
    background-color: rgba(34, 197, 94, 0.15) !important;
    border-left: 4px solid #22c55e !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

.stSuccess p {
    color: #dcfce7 !important;
}

.stWarning {
    background-color: rgba(234, 179, 8, 0.15) !important;
    border-left: 4px solid #eab308 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

.stWarning p {
    color: #fef3c7 !important;
}

.stError {
    background-color: rgba(239, 68, 68, 0.15) !important;
    border-left: 4px solid #ef4444 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}

.stError p {
    color: #fee2e2 !important;
}

/* Tabs Styling */
[role="tablist"] {
    border-bottom: 2px solid rgba(56, 189, 248, 0.2) !important;
}

button[role="tab"] {
    color: #cbd5e1 !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 500 !important;
}

button[role="tab"][aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}

/* Metric Styling */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(51, 65, 85, 0.5) 100%) !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

[data-testid="metric-container"] span {
    color: #e0e7ff !important;
}

/* Divider */
hr {
    border-color: rgba(56, 189, 248, 0.2) !important;
}

/* Dataframe Styling */
[data-testid="stDataframe"] {
    background-color: rgba(30, 41, 59, 0.5) !important;
}

/* Radio and Checkbox */
input[type="radio"], input[type="checkbox"] {
    accent-color: #38bdf8 !important;
}

/* Markdown text */
.stMarkdown {
    color: #e2e8f0 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HOME PAGE ----------------
if st.session_state.page == "home":

    # Real data queries from app state
    # get_all_international_matches returns (sorted_matches, live_api_ok, upcoming_api_ok)
    all_intl_matches, _live_api_ok_home, _upcoming_api_ok_home = get_all_international_matches()
    franchise_matches = get_franchise_matches()
    live_intl = [m for m in all_intl_matches if m.get("stage") == "Live"]
    upcoming_intl = [m for m in all_intl_matches if m.get("stage") == "Upcoming"]
    completed_intl = [m for m in all_intl_matches if m.get("stage") == "Completed"]
    total_active_fixtures = len(all_intl_matches) + len(franchise_matches)
    total_verified_players = len(INTERNATIONAL_PLAYERS_DATA)

    # Scoped Sports-Tech Cinematic Styling
    st.markdown("""
    <style>
    @keyframes pulseLiveDot {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    @keyframes pulseEmeraldDot {
        0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .cric-hero-container {
        background: radial-gradient(120% 100% at 50% 0%, rgba(14, 165, 233, 0.16) 0%, rgba(15, 23, 42, 0) 70%),
                    linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 15, 29, 0.98) 100%);
        border: 1px solid rgba(56, 189, 248, 0.22);
        border-radius: 24px;
        padding: 44px 32px 32px 32px;
        text-align: center;
        margin-bottom: 28px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.6), 0 0 45px -10px rgba(14, 165, 233, 0.2);
    }
    .cric-badge-strip {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 9999px;
        padding: 7px 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #38bdf8;
        text-transform: uppercase;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .cric-dot-live {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #ef4444;
        display: inline-block;
        animation: pulseLiveDot 1.8s infinite;
    }
    .cric-dot-emerald {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        display: inline-block;
        animation: pulseEmeraldDot 2s infinite;
    }
    .cric-hero-heading {
        font-size: 50px;
        line-height: 1.15;
        font-weight: 900;
        letter-spacing: -1px;
        margin-bottom: 16px;
        color: #f8fafc;
    }
    .cric-gradient-text {
        background: linear-gradient(135deg, #38bdf8 0%, #22d3ee 45%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .cric-hero-subtext {
        max-width: 860px;
        margin: 0 auto 24px auto;
        font-size: 16.5px;
        line-height: 1.65;
        color: #94a3b8;
        font-weight: 400;
    }

    /* Stat Cards */
    .cric-stat-box {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-radius: 18px;
        padding: 22px 18px;
        text-align: center;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
    }
    .cric-stat-box:hover {
        border-color: rgba(56, 189, 248, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 14px 35px -10px rgba(56, 189, 248, 0.25);
    }
    .cric-stat-value {
        font-size: 42px;
        font-weight: 900;
        line-height: 1.1;
        margin-bottom: 6px;
        background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .cric-stat-title {
        font-size: 12.5px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #38bdf8;
        margin-bottom: 6px;
    }
    .cric-stat-sub {
        font-size: 12px;
        color: #64748b;
        line-height: 1.4;
    }

    /* Section Headers */
    .cric-section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 36px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }
    .cric-pill {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .cric-pill-live { background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }
    .cric-pill-cyan { background: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.35); }
    .cric-pill-purple { background: rgba(168, 85, 247, 0.18); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.35); }
    .cric-pill-blue { background: rgba(59, 130, 246, 0.18); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.35); }

    .cric-section-name {
        font-size: 22px;
        font-weight: 800;
        color: #f1f5f9;
        margin: 0;
    }

    /* Glass Cards */
    .cric-glass-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.72) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(56, 189, 248, 0.18);
        border-radius: 18px;
        padding: 22px;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        margin-bottom: 10px;
    }
    .cric-glass-card:hover {
        border-color: rgba(56, 189, 248, 0.45);
        transform: translateY(-4px);
        box-shadow: 0 12px 35px -10px rgba(56, 189, 248, 0.2);
    }
    .cric-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }
    .cric-card-badge {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 6px;
        background: rgba(15, 23, 42, 0.7);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    .cric-match-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .cric-team-text {
        font-size: 16px;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .cric-score-text {
        font-size: 17px;
        font-weight: 800;
        color: #38bdf8;
    }
    .cric-status-box {
        background: rgba(15, 23, 42, 0.65);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12.5px;
        font-weight: 600;
        color: #cbd5e1;
        margin-top: 12px;
    }

    /* Player mini badge */
    .cric-player-stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 12px;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(56, 189, 248, 0.12);
    }
    .cric-player-stat-item {
        text-align: center;
    }
    .cric-player-stat-val {
        font-size: 15px;
        font-weight: 800;
        color: #38bdf8;
    }
    .cric-player-stat-lbl {
        font-size: 10.5px;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. HERO SECTION
    st.markdown("""
    <div class="cric-hero-container">
        <div class="cric-badge-strip">
            <span class="cric-dot-live"></span> RADAR LIVE &nbsp;•&nbsp; <span class="cric-dot-emerald"></span> 9,000+ REAL ICC MATCHES &nbsp;•&nbsp; DUAL RF AI
        </div>
        <div class="cric-hero-heading">
            NEXT-GEN <span class="cric-gradient-text">CRICKET ANALYTICS</span> TERMINAL
        </div>
        <div class="cric-hero-subtext">
            A unified cinematic sports-technology intelligence workspace combining real-time international coverage,
            verified player career intelligence for Men's & Women's stars, enterprise relational SQL analytics,
            and machine learning predictive modeling.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Action Bar
    h_col1, h_col2, h_col3, h_col4 = st.columns(4)
    with h_col1:
        st.button("⚡ Live Match Radar", key="hero_btn_live", on_click=navigate_page, args=("live",))
    with h_col2:
        st.button("🤖 ML Match Predictor", key="hero_btn_ml", on_click=navigate_page, args=("ml",))
    with h_col3:
        st.button("📊 Player Analytics", key="hero_btn_players", on_click=navigate_page, args=("players",))
    with h_col4:
        st.button("📈 Data Visualizations", key="hero_btn_viz", on_click=navigate_page, args=("visualizations",))

    # 2. LARGE PROJECT STATISTICS
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st_c1, st_c2, st_c3, st_c4 = st.columns(4)

    with st_c1:
        st.markdown("""
        <div class="cric-stat-box">
            <div class="cric-stat-value">9,000+</div>
            <div class="cric-stat-title">HISTORICAL ICC MATCHES</div>
            <div class="cric-stat-sub">Official Cricsheet international match repository training set</div>
        </div>
        """, unsafe_allow_html=True)

    with st_c2:
        st.markdown(f"""
        <div class="cric-stat-box">
            <div class="cric-stat-value">{total_active_fixtures}</div>
            <div class="cric-stat-title">FIXTURES & LEAGUES</div>
            <div class="cric-stat-sub">{len(live_intl)} live, {len(upcoming_intl)} upcoming, and {len(completed_intl)} recent completed encounters</div>
        </div>
        """, unsafe_allow_html=True)

    with st_c3:
        st.markdown(f"""
        <div class="cric-stat-box">
            <div class="cric-stat-value">{total_verified_players}</div>
            <div class="cric-stat-title">VERIFIED ICC STARS</div>
            <div class="cric-stat-sub">Test, ODI, and T20I verified career profiles across Men's & Women's cricket</div>
        </div>
        """, unsafe_allow_html=True)

    with st_c4:
        st.markdown("""
        <div class="cric-stat-box">
            <div class="cric-stat-value">25</div>
            <div class="cric-stat-title">RELATIONAL SQL QUERIES</div>
            <div class="cric-stat-sub">Multi-table relational schema with JOINs, aggregations, and window analytics</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. LIVE CRICKET INTELLIGENCE SHOWCASE
    st.markdown("""
    <div class="cric-section-header">
        <span class="cric-pill cric-pill-live">🔴 LIVE RADAR</span>
        <h3 class="cric-section-name">Featured International & Franchise Encounters</h3>
    </div>
    """, unsafe_allow_html=True)

    feat_matches = all_intl_matches[:2] if all_intl_matches else []
    if feat_matches:
        lm_c1, lm_c2 = st.columns(2)
        for idx, (col, match) in enumerate(zip([lm_c1, lm_c2], feat_matches)):
            with col:
                t1 = match.get("team1", "Team 1")
                t2 = match.get("team2", "Team 2")
                f1 = match.get("team1_flag", "🏏")
                f2 = match.get("team2_flag", "🏏")
                s1 = match.get("score1") or "Fixture"
                s2 = match.get("score2") or "Fixture"
                fmt = match.get("format", "T20I")
                gen = match.get("gender", "Men's")
                status = match.get("status", "Match scheduled")
                venue = match.get("venue", "International Stadium")
                stage = match.get("stage", "Live")
                stage_color = "#ef4444" if stage == "Live" else ("#eab308" if stage == "Upcoming" else "#10b981")

                st.markdown(f"""
                <div class="cric-glass-card">
                    <div class="cric-card-top">
                        <span class="cric-card-badge">{match.get('series', 'ICC Championship')} • {fmt} ({gen})</span>
                        <span style="color: {stage_color}; font-size: 11.5px; font-weight: 800; letter-spacing: 0.5px;">● {stage.upper()}</span>
                    </div>
                    <div class="cric-match-line">
                        <span class="cric-team-text">{f1} {t1}</span>
                        <span class="cric-score-text">{s1}</span>
                    </div>
                    <div class="cric-match-line">
                        <span class="cric-team-text">{f2} {t2}</span>
                        <span class="cric-score-text">{s2}</span>
                    </div>
                    <div class="cric-status-box">
                        📍 {venue}<br>
                        <span style="color:#38bdf8; font-weight:700;">{status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"View Match Details #{idx+1} ➔", key=f"view_live_card_{idx}", on_click=navigate_page, args=("live",))

    # 4. PLAYER ANALYTICS SHOWCASE
    st.markdown("""
    <div class="cric-section-header">
        <span class="cric-pill cric-pill-cyan">📊 PLAYER INTELLIGENCE</span>
        <h3 class="cric-section-name">Official ICC Career Records & Spotlight Stars</h3>
    </div>
    """, unsafe_allow_html=True)

    spotlight_names = ["Virat Kohli", "Ellyse Perry", "Jasprit Bumrah"]
    sp_c1, sp_c2, sp_c3 = st.columns(3)

    for col, p_name in zip([sp_c1, sp_c2, sp_c3], spotlight_names):
        p_data = INTERNATIONAL_PLAYERS_DATA.get(p_name)
        if p_data:
            with col:
                country = p_data.get("country", "")
                role = p_data.get("role", "")
                flag = TEAM_FLAGS.get(country, "🏏")
                bat = p_data.get("batting_career", {})
                bowl = p_data.get("bowling_career", {})

                total_runs = sum(bat.get(f, {}).get("runs", 0) for f in ["Test", "ODI", "T20I"])
                total_100s = sum(bat.get(f, {}).get("100s", 0) for f in ["Test", "ODI", "T20I"])
                total_wkts = sum(bowl.get(f, {}).get("wickets", 0) for f in ["Test", "ODI", "T20I"])
                odi_avg = bat.get("ODI", {}).get("average", 0.0)

                st.markdown(f"""
                <div class="cric-glass-card">
                    <div class="cric-card-top">
                        <span class="cric-card-badge">{flag} {country} • {p_data.get('gender', "Men's")}</span>
                        <span style="color: #38bdf8; font-size: 11px; font-weight: 700;">VERIFIED ICC</span>
                    </div>
                    <div style="font-size: 19px; font-weight: 800; color: #f8fafc; margin-bottom: 2px;">{p_name}</div>
                    <div style="font-size: 12.5px; color: #94a3b8; margin-bottom: 12px;">{role}</div>
                    <div class="cric-player-stat-grid">
                        <div class="cric-player-stat-item">
                            <div class="cric-player-stat-val">{total_runs:,}</div>
                            <div class="cric-player-stat-lbl">Runs</div>
                        </div>
                        <div class="cric-player-stat-item">
                            <div class="cric-player-stat-val">{total_100s if total_100s > 0 else total_wkts}</div>
                            <div class="cric-player-stat-lbl">{"100s" if total_100s > 0 else "Wickets"}</div>
                        </div>
                        <div class="cric-player-stat-item">
                            <div class="cric-player-stat-val">{odi_avg:.1f}</div>
                            <div class="cric-player-stat-lbl">ODI Avg</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"Inspect {p_name.split()[0]} Stats ➔", key=f"btn_p_{p_name.replace(' ', '_')}", on_click=navigate_page, args=("players",))

    # 5. MACHINE LEARNING & PREDICTION + DATA VISUALIZATION
    st.markdown("""
    <div class="cric-section-header">
        <span class="cric-pill cric-pill-purple">🤖 PREDICTIVE AI & VISUAL ANALYTICS</span>
        <h3 class="cric-section-name">Machine Learning Modeling & Interactive Plotly Charts</h3>
    </div>
    """, unsafe_allow_html=True)

    tech_c1, tech_c2 = st.columns(2)

    with tech_c1:
        st.markdown("""
        <div class="cric-glass-card">
            <div class="cric-card-top">
                <span class="cric-card-badge">RANDOM FOREST PIPELINE</span>
                <span style="color: #c084fc; font-size: 11px; font-weight: 800;">HELD-OUT 20% SPLIT</span>
            </div>
            <div style="font-size: 20px; font-weight: 800; color: #f8fafc; margin-bottom: 8px;">
                🤖 Dual-Model Match Outcome Engine
            </div>
            <p style="color: #cbd5e1; font-size: 13.5px; line-height: 1.5; margin-bottom: 14px;">
                Trains on 9,000+ ICC international matches to forecast winner probabilities and projected runs based on team head-to-head records, venue dynamics, match format, and gender categorization.
            </p>
            <div style="background: rgba(15, 23, 42, 0.65); border-radius: 10px; padding: 12px; border: 1px solid rgba(168, 85, 247, 0.2); font-size: 12.5px; color: #cbd5e1;">
                ✔ <b>Match Winner Classifier:</b> Calibrated win probabilities (0–100%)<br>
                ✔ <b>Score Regressor:</b> Historical pitch & format projected innings totals<br>
                ✔ <b>Safety Architecture:</b> Zero crashes on sparse venue/score splits
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("🔮 Open Machine Learning Predictor ➔", key="home_ml_engine_btn", on_click=navigate_page, args=("ml",))

    with tech_c2:
        st.markdown("""
        <div class="cric-glass-card">
            <div class="cric-card-top">
                <span class="cric-card-badge">PLOTLY DARK SUITE</span>
                <span style="color: #34d399; font-size: 11px; font-weight: 800;">6 INTERACTIVE SUITES</span>
            </div>
            <div style="font-size: 20px; font-weight: 800; color: #f8fafc; margin-bottom: 8px;">
                📈 Deep Data Visualizations & Dashboards
            </div>
            <p style="color: #cbd5e1; font-size: 13.5px; line-height: 1.5; margin-bottom: 14px;">
                Interactive high-contrast charts analyzing match patterns, format scoring spreads, toss impact ratios, and team win percentages rendered via Plotly Dark styling.
            </p>
            <div style="background: rgba(15, 23, 42, 0.65); border-radius: 10px; padding: 12px; border: 1px solid rgba(16, 185, 129, 0.2); font-size: 12.5px; color: #cbd5e1;">
                ✔ <b>Run Distribution:</b> Test, ODI & T20 scoring spread analysis<br>
                ✔ <b>Toss & Venue Impact:</b> Batting vs bowling first historical win rates<br>
                ✔ <b>Performance Metrics:</b> International team victory trends
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("📈 Launch Interactive Visualizations ➔", key="home_viz_engine_btn", on_click=navigate_page, args=("visualizations",))

    # 6. ENTERPRISE NAVIGATION TERMINALS (Action Grid)
    st.markdown("""
    <div class="cric-section-header">
        <span class="cric-pill cric-pill-blue">🎛️ PLATFORM MODULES</span>
        <h3 class="cric-section-name">Direct Terminal Navigation</h3>
    </div>
    """, unsafe_allow_html=True)

    nav_row1_c1, nav_row1_c2, nav_row1_c3 = st.columns(3)
    nav_row2_c1, nav_row2_c2, nav_row2_c3 = st.columns(3)

    with nav_row1_c1:
        st.markdown("""
        <div class="cric-glass-card">
            <div style="font-size: 28px; margin-bottom: 8px;">⚡</div>
            <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">Live Matches</div>
            <p style="color: #94a3b8; font-size: 13px; line-height: 1.4; margin-bottom: 12px;">Real-time international and premier franchise match scores and schedules.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Launch Live Matches", key="term_btn_live", on_click=navigate_page, args=("live",))

    with nav_row1_c2:
        st.markdown("""
        <div class="cric-glass-card">
            <div style="font-size: 28px; margin-bottom: 8px;">📊</div>
            <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">Player Stats</div>
            <p style="color: #94a3b8; font-size: 13px; line-height: 1.4; margin-bottom: 12px;">Career batting and bowling figures across formats for global superstars.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Launch Player Stats", key="term_btn_players", on_click=navigate_page, args=("players",))

    with nav_row1_c3:
        st.markdown("""
        <div class="cric-glass-card">
            <div style="font-size: 28px; margin-bottom: 8px;">🤖</div>
            <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">ML Prediction</div>
            <p style="color: #94a3b8; font-size: 13px; line-height: 1.4; margin-bottom: 12px;">Random Forest algorithm predicting match winners and projected scores.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Launch ML Engine", key="term_btn_ml", on_click=navigate_page, args=("ml",))

    with nav_row2_c1:
        st.markdown("""
        <div class="cric-glass-card">
            <div style="font-size: 28px; margin-bottom: 8px;">📈</div>
            <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">Visualizations</div>
            <p style="color: #94a3b8; font-size: 13px; line-height: 1.4; margin-bottom: 12px;">Interactive dark-themed charts and dynamic analytical cricket graphs.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Launch Visualizations", key="term_btn_viz", on_click=navigate_page, args=("visualizations",))

    with nav_row2_c2:
        st.markdown("""
        <div class="cric-glass-card">
            <div style="font-size: 28px; margin-bottom: 8px;">🔍</div>
            <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">SQL Analytics</div>
            <p style="color: #94a3b8; font-size: 13px; line-height: 1.4; margin-bottom: 12px;">Execute 25 optimized relational queries with live table and metric outputs.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Launch SQL Analytics", key="term_btn_sql", on_click=navigate_page, args=("sql",))

    with nav_row2_c3:
        st.markdown("""
        <div class="cric-glass-card">
            <div style="font-size: 28px; margin-bottom: 8px;">⚙️</div>
            <div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin-bottom: 4px;">CRUD & Database</div>
            <p style="color: #94a3b8; font-size: 13px; line-height: 1.4; margin-bottom: 12px;">Create, update, inspect and manage relational teams, venues and match records.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Launch CRUD Manager", key="term_btn_crud", on_click=navigate_page, args=("crud",))


# ---------------- LIVE PAGE ----------------
elif st.session_state.page == "live":

    st.markdown('<div class="title">⚡ Live Cricket Matches</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Real-time Scores & International Fixtures for Men\'s & Women\'s National Teams</div>', unsafe_allow_html=True)

    head_col1, head_col2 = st.columns([6, 1])
    with head_col1:
        st.caption("🌐 Verified Official Match Feed | Focus on Recognized ICC National Cricket & Separate Franchise Leagues")
    with head_col2:
        if st.button("🔄 Refresh", key="refresh_live_btn"):
            st.rerun()

    # Load match datasets — now returns (matches, live_api_ok, upcoming_api_ok)
    all_intl_matches, live_api_ok, upcoming_api_ok = get_all_international_matches()
    franchise_matches = get_franchise_matches()

    # Show honest data-availability notice when the live API is not connected
    if not live_api_ok:
        st.warning(
            "⚠️ **Live data currently unavailable** — current scores could not be verified. "
            "Configure a valid `RAPIDAPI_KEY` to receive real-time international match data. "
            "Historical completed records are still shown below."
        )
    elif not upcoming_api_ok:
        st.warning(
            "⚠️ **Upcoming fixture data currently unavailable** — schedule data could not be verified. "
            "Live and completed records are still shown below."
        )

    # Separate counts for summary metric badges
    india_matches = [m for m in all_intl_matches if "India" in m.get("team1", "") or "India" in m.get("team2", "")]
    mens_intl = [m for m in all_intl_matches if m.get("gender") == "Men's"]
    womens_intl = [m for m in all_intl_matches if m.get("gender") == "Women's"]
    live_intl = [m for m in all_intl_matches if m.get("stage") == "Live"]

    # Summary metrics row
    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    with mcol1:
        st.metric("🔴 Live International", len(live_intl))
    with mcol2:
        st.metric("🇮🇳 Team India Matches", len(india_matches))
    with mcol3:
        st.metric("🏏 Men's International", len(mens_intl))
    with mcol4:
        st.metric("🌸 Women's International", len(womens_intl))
    with mcol5:
        st.metric("🏆 Franchise Fixtures", len(franchise_matches))

    st.markdown("---")

    # Main category tabs - Keeping Franchise strictly separate from International
    tab_intl, tab_franchise, tab_api_status = st.tabs([
        "🌐 International Cricket (National Teams)",
        "🏆 Franchise Leagues (IPL / WPL / BBL)",
        "📡 API Status & Coverage"
    ])

    # ---------------- TAB 1: INTERNATIONAL CRICKET ----------------
    with tab_intl:
        st.markdown("### 🌐 ICC International Cricket (Men's & Women's National Teams)")
        st.caption("Strictly filtered to recognized national teams (India, Australia, England, South Africa, NZ, Pakistan, Sri Lanka, Bangladesh, Afghanistan, West Indies, etc.). Club, academy, and A-team matches are removed.")

        intl_filter = st.radio(
            "Filter International Matches:",
            ["🌟 All International", "🏏 Men's International", "🌸 Women's International", "🔴 Live Only", "⏳ Upcoming Fixtures", "✅ Completed Results"],
            horizontal=True,
            key="intl_filter_radio"
        )

        filtered_intl = all_intl_matches
        if intl_filter == "🏏 Men's International":
            filtered_intl = [m for m in filtered_intl if m.get("gender") == "Men's"]
        elif intl_filter == "🌸 Women's International":
            filtered_intl = [m for m in filtered_intl if m.get("gender") == "Women's"]
        elif intl_filter == "🔴 Live Only":
            filtered_intl = [m for m in filtered_intl if m.get("stage") == "Live"]
        elif intl_filter == "⏳ Upcoming Fixtures":
            filtered_intl = [m for m in filtered_intl if m.get("stage") == "Upcoming"]
        elif intl_filter == "✅ Completed Results":
            filtered_intl = [m for m in filtered_intl if m.get("stage") == "Completed"]

        sorted_intl = sorted(
            filtered_intl,
            key=lambda x: (x.get("priority", 3), 0 if x.get("stage") == "Live" else (1 if x.get("stage") == "Upcoming" else 2))
        )

        if not sorted_intl:
            if intl_filter == "🔴 Live Only" and not live_api_ok:
                st.warning("🔴 **Live data currently unavailable** — current scores could not be verified. Configure a valid `RAPIDAPI_KEY` to receive real-time match data.")
            elif intl_filter == "⏳ Upcoming Fixtures" and not upcoming_api_ok:
                st.warning("⏳ **Upcoming schedule data currently unavailable** — fixture data could not be verified. Configure a valid `RAPIDAPI_KEY` for live schedule data.")
            elif intl_filter in ("🔴 Live Only", "⏳ Upcoming Fixtures") and (live_api_ok or upcoming_api_ok):
                st.info("No matches found for the selected filter at this moment.")
            else:
                st.info("No international matches match the selected filter.")
        else:
            for match in sorted_intl:
                is_india = "India" in match.get("team1", "") or "India" in match.get("team2", "")
                gender = match.get("gender", "Men's")
                stage = match.get("stage", "Live")
                fmt = match.get("format", "T20I")

                stage_badge = "🔴 LIVE" if stage == "Live" else ("⏳ UPCOMING" if stage == "Upcoming" else "✅ COMPLETED")
                stage_color = "#ef4444" if stage == "Live" else ("#eab308" if stage == "Upcoming" else "#10b981")
                gender_color = "#38bdf8" if gender == "Men's" else "#f472b6"

                card_border = "2px solid #f59e0b" if is_india else "1px solid rgba(56, 189, 248, 0.25)"
                card_bg = "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%)"

                t1_flag = match.get("team1_flag", "🏏")
                t2_flag = match.get("team2_flag", "🏏")
                t1_name = match.get("team1", "")
                t2_name = match.get("team2", "")

                score1_str = match.get("score1", "")
                score2_str = match.get("score2", "")
                status_str = match.get("status", "")
                venue_str = match.get("venue", "International Stadium")
                series_str = match.get("series", "ICC International Series")
                date_str = match.get("date", "")
                source_str = match.get("source", "Live match data")
                if "broadcast" in source_str.lower():
                    source_str = "Live match data"
                source_url = match.get("source_url") or match.get("url")
                if source_url and str(source_url).startswith("http"):
                    source_html = f'<a href="{source_url}" target="_blank" style="color: #38bdf8; text-decoration: underline;">{source_str}</a>'
                else:
                    source_html = f'<span style="color: #64748b;">Source: {source_str}</span>'

                india_highlight_html = '<span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 11px; margin-right: 8px;">🇮🇳 TEAM INDIA HIGHLIGHT</span>' if is_india else ""

                st.markdown(f"""
                <div style="background: {card_bg}; border: {card_border}; border-radius: 12px; padding: 18px 22px; margin-bottom: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
                        <div>
                            {india_highlight_html}
                            <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">{fmt}</span>
                            <span style="background: rgba(244, 114, 182, 0.15); color: {gender_color}; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-left: 6px;">{gender}</span>
                            <span style="color: #94a3b8; font-size: 13px; margin-left: 10px;">{series_str}</span>
                        </div>
                        <div>
                            <span style="background: rgba(0,0,0,0.3); color: {stage_color}; border: 1px solid {stage_color}; padding: 2px 10px; border-radius: 12px; font-weight: 700; font-size: 12px;">{stage_badge}</span>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin: 12px 0; flex-wrap: wrap;">
                        <div style="font-size: 18px; font-weight: 700; color: #f8fafc;">
                            <span style="font-size: 24px; margin-right: 6px;">{t1_flag}</span> {t1_name}
                            <span style="color: #38bdf8; margin-left: 10px; font-size: 19px;">{score1_str}</span>
                        </div>
                        <div style="color: #64748b; font-weight: 700; font-size: 14px; padding: 0 12px;">VS</div>
                        <div style="font-size: 18px; font-weight: 700; color: #f8fafc;">
                            <span style="font-size: 24px; margin-right: 6px;">{t2_flag}</span> {t2_name}
                            <span style="color: #38bdf8; margin-left: 10px; font-size: 19px;">{score2_str}</span>
                        </div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 8px 12px; border-radius: 6px; margin-top: 10px;">
                        <div style="color: #f1f5f9; font-weight: 600; font-size: 14px;">📡 {status_str}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 12px; margin-top: 10px; flex-wrap: wrap;">
                        <span>📍 {venue_str}</span>
                        <span>🗓️ {date_str} | {source_html}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ---------------- TAB 2: FRANCHISE LEAGUES (IPL / WPL / BBL) ----------------
    with tab_franchise:
        st.markdown("### 🏆 Franchise & T20 Leagues (Kept Strictly Separate)")
        st.caption("Franchise competitions (IPL, WPL, BBL, WBBL, PSL) are managed in this dedicated section and isolated from national international fixtures.")

        fran_filter = st.radio(
            "Filter Franchise Matches:",
            ["🌟 All Franchise", "🇮🇳 IPL (Men's)", "🌸 WPL (Women's Premier League)", "🇦🇺 BBL / WBBL", "🇵🇰 PSL / Other"],
            horizontal=True,
            key="fran_filter_radio"
        )

        filtered_fran = franchise_matches
        if fran_filter == "🇮🇳 IPL (Men's)":
            filtered_fran = [m for m in filtered_fran if "IPL" in m.get("series", "") and m.get("gender") == "Men's"]
        elif fran_filter == "🌸 WPL (Women's Premier League)":
            filtered_fran = [m for m in filtered_fran if "WPL" in m.get("series", "") or m.get("gender") == "Women's"]
        elif fran_filter == "🇦🇺 BBL / WBBL":
            filtered_fran = [m for m in filtered_fran if "BBL" in m.get("series", "") or "Big Bash" in m.get("series", "")]
        elif fran_filter == "🇵🇰 PSL / Other":
            filtered_fran = [m for m in filtered_fran if "PSL" in m.get("series", "")]

        if not filtered_fran:
            st.info("No franchise matches match the selected filter.")
        else:
            for match in filtered_fran:
                gender = match.get("gender", "Men's")
                series_str = match.get("series", "Franchise League")
                t1_name = match.get("team1", "")
                t2_name = match.get("team2", "")
                t1_flag = match.get("team1_flag", "🏏")
                t2_flag = match.get("team2_flag", "🏏")
                score1_str = match.get("score1", "")
                score2_str = match.get("score2", "")
                status_str = match.get("status", "")
                venue_str = match.get("venue", "Franchise Stadium")
                date_str = match.get("date", "")
                gender_color = "#38bdf8" if gender == "Men's" else "#f472b6"

                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.6) 100%); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 12px; padding: 18px 22px; margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div>
                            <span style="background: rgba(14, 165, 233, 0.2); color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">{series_str}</span>
                            <span style="background: rgba(244, 114, 182, 0.15); color: {gender_color}; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; margin-left: 6px;">{gender}</span>
                        </div>
                        <span style="background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700;">FRANCHISE MATCH</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin: 12px 0; flex-wrap: wrap;">
                        <div style="font-size: 17px; font-weight: 700; color: #f8fafc;">
                            <span style="font-size: 20px; margin-right: 6px;">{t1_flag}</span> {t1_name}
                            <span style="color: #38bdf8; margin-left: 8px;">{score1_str}</span>
                        </div>
                        <div style="color: #64748b; font-weight: 700; font-size: 13px; padding: 0 10px;">VS</div>
                        <div style="font-size: 17px; font-weight: 700; color: #f8fafc;">
                            <span style="font-size: 20px; margin-right: 6px;">{t2_flag}</span> {t2_name}
                            <span style="color: #38bdf8; margin-left: 8px;">{score2_str}</span>
                        </div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.5); padding: 8px 12px; border-radius: 6px; margin-top: 8px;">
                        <div style="color: #f1f5f9; font-weight: 600; font-size: 13px;">🏆 {status_str}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 12px; margin-top: 8px;">
                        <span>📍 {venue_str}</span>
                        <span>🗓️ {date_str}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ---------------- TAB 3: API STATUS & COVERAGE ----------------
    with tab_api_status:
        st.markdown("### 📡 API Verification & Data Source Diagnostics")

        api_key = get_rapidapi_key()
        has_key = bool(api_key and len(api_key) > 5)

        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.markdown("**Cricbuzz RapidAPI Status:**")
            if has_key:
                st.success("✅ RapidAPI Key configured. Live endpoint active.")
            else:
                st.warning(
                    "⚠️ RapidAPI Key not configured. **Live data currently unavailable** — "
                    "current scores could not be verified. LIVE and UPCOMING matches will show empty "
                    "until a valid `RAPIDAPI_KEY` is set. Historical completed records are still "
                    "available via the local database (for Completed matches only)."
                )

            st.markdown("""
            - **Live Endpoint**: `https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live`
            - **Upcoming Endpoint**: `https://cricbuzz-cricket.p.rapidapi.com/matches/v1/upcoming`
            - **Recent Endpoint**: `https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent`
            """)

        with col_stat2:
            st.markdown("**New Cricket API Free Data Evaluation:**")
            st.info("ℹ️ Evaluation check: 'Cricket API Free Data' is not pre-configured in project environment. The working Cricbuzz API and verified Cricsheet historical international dataset are preserved to ensure 100% reliable international Men's & Women's cricket coverage.")

            # Database stats
            try:
                conn = sqlite3.connect("cricket.db")
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM ml_international_matches WHERE gender = 'men'")
                m_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM ml_international_matches WHERE gender = 'women'")
                w_cnt = c.fetchone()[0]
                conn.close()
                st.markdown(f"""
                - **Verified Men's International Matches**: `{m_cnt:,}`
                - **Verified Women's International Matches**: `{w_cnt:,}`
                - **Total International Matches**: `{m_cnt + w_cnt:,}`
                - **Club / A-Team matches in International section**: `0 (Strictly Blocked)`
                """)
            except Exception as e:
                st.write(f"DB check: {e}")

    st.markdown("---")
    st.button("⬅ Back to Home", key="back_live", on_click=navigate_page, args=("home",))

# ---------------- SQL PAGE ----------------
elif st.session_state.page == "sql":

    st.title("🔍 SQL Analytics Dashboard")

    st.markdown("""
    ### Comprehensive SQL Query Analysis
    Run 25 SQL queries across both legacy and enhanced database schemas.
    """)

    # Query Categories Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Legacy Queries (1-5)", "🏆 Enhanced Queries (6-15)", "⚡ Advanced Queries (16-25)"])

    # ==================== LEGACY QUERIES TAB ====================
    with tab1:
        st.subheader("Legacy Database Queries")
        st.markdown("Queries using the original 'matches' table")

        query_options = {
            "Query 1: All Matches": query_1_all_matches,
            "Query 2: Total Matches Count": query_2_total_matches,
            "Query 3: Matches by Status": query_3_matches_by_status,
            "Query 4: Team1 Display": query_4_team1_matches,
            "Query 5: Recent Matches": query_5_recent_matches,
        }

        selected_query = st.selectbox("Select Query", list(query_options.keys()), key="legacy_query")

        if st.button("Run Query", key="run_legacy"):
            try:
                results, columns = query_options[selected_query]()
                if results:
                    df = pd.DataFrame(results, columns=columns)
                    st.dataframe(df, use_container_width=True)
                    st.success(f"✅ Query executed successfully! Found {len(results)} records.")
                else:
                    st.warning("⚠️ No results found for this query.")
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")

    # ==================== ENHANCED QUERIES TAB ====================
    with tab2:
        st.subheader("Enhanced Database Queries")
        st.markdown("Queries using the new relational schema (teams, players, venues, matches_enhanced)")

        query_options = {
            "Query 6: All Teams": query_6_all_teams,
            "Query 7: Players with Teams": query_7_all_players_with_teams,
            "Query 8: Team Player Count": query_8_team_player_count,
            "Query 9: Venues by Country": query_9_venues_by_country,
            "Query 10: Batsmen Only": query_10_batsmen_only,
            "Query 11: Bowlers Only": query_11_bowlers_only,
            "Query 12: All-rounders": query_12_all_rounders,
            "Query 13: Venue Capacity Analysis": query_13_venue_capacity_analysis,
            "Query 14: Players by Nationality": query_14_players_by_nationality,
            "Query 15: Team Captains": query_15_team_captains,
        }

        selected_query = st.selectbox("Select Query", list(query_options.keys()), key="enhanced_query")

        if st.button("Run Query", key="run_enhanced"):
            try:
                results, columns = query_options[selected_query]()
                if results:
                    df = pd.DataFrame(results, columns=columns)
                    st.dataframe(df, use_container_width=True)
                    st.success(f"✅ Query executed successfully! Found {len(results)} records.")
                else:
                    st.warning("⚠️ No results found for this query.")
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")

    # ==================== ADVANCED QUERIES TAB ====================
    with tab3:
        st.subheader("Advanced Database Queries")
        st.markdown("Complex queries using JOINs, aggregations, and advanced SQL features")

        query_options = {
            "Query 16: Enhanced Matches Overview": query_16_enhanced_matches_overview,
            "Query 17: Matches by Venue": query_17_matches_by_venue,
            "Query 18: Player Roles Distribution": query_18_player_roles_distribution,
            "Query 19: Teams with Most Players": query_19_teams_with_most_players,
            "Query 20: Venues by Pitch Type": query_20_venues_by_pitch_type,
            "Query 21: Players Without Team": query_21_players_without_team,
            "Query 22: Matches Without Venue": query_22_matches_without_venue,
            "Query 23: Complete Team Info": query_23_complete_team_info,
            "Query 24: Venue Match Analysis": query_24_venue_match_analysis,
            "Query 25: Database Summary": query_25_comprehensive_database_summary,
        }

        selected_query = st.selectbox("Select Query", list(query_options.keys()), key="advanced_query")

        if st.button("Run Query", key="run_advanced"):
            try:
                results, columns = query_options[selected_query]()
                if results:
                    df = pd.DataFrame(results, columns=columns)
                    st.dataframe(df, use_container_width=True)
                    st.success(f"✅ Query executed successfully! Found {len(results)} records.")
                else:
                    st.warning("⚠️ No results found for this query.")
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")

    # Query Statistics
    st.markdown("---")
    st.subheader("📈 Query Statistics")

    col1, col2, col3 = st.columns(3)

    with col2:
        st.metric("Enhanced Queries", "10", "Relational SQL")

    with col3:
        st.metric("Advanced Queries", "10", "Complex SQL")

    st.info("💡 **Tip:** Enhanced queries use JOINs and relationships between tables for more powerful analytics!")

    st.button("⬅ Back", key="back_sql", on_click=navigate_page, args=("home",))

# ---------------- ML PREDICTION PAGE ----------------
elif st.session_state.page == "ml":

    # ─────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────
    ml_hdr1, ml_hdr2 = st.columns([6, 1])
    with ml_hdr1:
        st.markdown('<div class="title">🤖 ML Match Prediction</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class=\"subtitle\">Trained on 9,000+ real ICC international matches "
            "(Men's &amp; Women's) from Cricsheet historical data</div>",
            unsafe_allow_html=True
        )
    with ml_hdr2:
        st.button("⬅ Back", key="back_ml_top", on_click=navigate_page, args=("home",))

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # LOAD MODEL  (cached — trains only once per Streamlit session)
    # ─────────────────────────────────────────────────────────
    try:
        with st.spinner("Loading ML model — first run trains on historical data (~10s)..."):
            bundle = load_ml_model_bundle()

        teams   = bundle.get("teams",   [])
        formats = bundle.get("formats", [])
        genders = bundle.get("genders", [])
        venues  = bundle.get("venues",  [])

        if not teams or not formats or not venues:
            st.warning("⚠️ No training data found. Run `historical_data_collector.py` to populate the database.")
        else:

            # ─────────────────────────────────────────────────
            # GENDER LABELS  (DB stores "men"/"women" lowercase)
            # ─────────────────────────────────────────────────
            _GENDER_LABEL = {"men": "Men's", "women": "Women's"}
            _GENDER_DB    = {"Men's": "men",  "Women's": "women"}
            raw_gender_map = {
                _GENDER_LABEL.get(str(g).strip().lower(), str(g).title()): g
                for g in sorted(genders)
            } if genders else {}
            gender_display_opts = list(raw_gender_map.keys()) if raw_gender_map else ["Men's", "Women's"]

            # ─────────────────────────────────────────────────
            # PREDICTION FORM
            # ─────────────────────────────────────────────────
            st.subheader("🏏 Configure Match")

            form_c1, form_c2, form_c3 = st.columns(3)

            with form_c1:
                gender_label = st.selectbox(
                    "🚻 Gender", gender_display_opts, key="ml_gender"
                )
                gender_db = raw_gender_map.get(gender_label, _GENDER_DB.get(gender_label, gender_label.lower()))

                match_format = st.selectbox(
                    "🏆 Format", sorted(formats), key="ml_format"
                )

            with form_c2:
                team1 = st.selectbox("🏳️ Team 1", teams, key="ml_team1")

            with form_c3:
                default_t2_idx = 1 if len(teams) > 1 else 0
                team2 = st.selectbox(
                    "🏳️ Team 2", teams,
                    index=default_t2_idx,
                    key="ml_team2"
                )

            venue = st.selectbox("🏟️ Venue", venues, key="ml_venue")

            if team1 == team2:
                st.warning("⚠️ Please select two **different** teams.")

            predict_btn = st.button(
                "🔮 Predict Match Outcome",
                key="ml_predict_btn",
                disabled=(team1 == team2)
            )

            # ─────────────────────────────────────────────────
            # PREDICTION RESULT
            # ─────────────────────────────────────────────────
            if predict_btn and team1 != team2:
                try:
                    result = predict_match(
                        team1=team1,
                        team2=team2,
                        match_format=match_format,
                        venue=venue,
                        gender=gender_db,
                        bundle=bundle
                    )

                    winner     = result["winner"]
                    confidence = result["confidence"]
                    t1_prob    = result["team1_probability"]
                    t2_prob    = result["team2_probability"]
                    t1_runs    = result["team1_runs"]
                    t2_runs    = result["team2_runs"]

                    st.markdown("---")

                    # Winner banner
                    trophy_color = "#27ae60" if winner == team1 else "#2980b9"
                    st.markdown(
                        f'<div style="background:{trophy_color};color:white;padding:18px 24px;'
                        f'border-radius:12px;text-align:center;font-size:1.4rem;'
                        f'font-weight:700;margin-bottom:16px;">'
                        f'🏆 Predicted Winner: {winner}</div>',
                        unsafe_allow_html=True
                    )

                    # KPI row
                    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                    with kpi1:
                        st.metric("🏆 Winner", winner)
                    with kpi2:
                        st.metric("🎯 Confidence", f"{confidence * 100:.1f}%")
                    with kpi3:
                        st.metric(f"{team1} Win %", f"{t1_prob * 100:.1f}%")
                    with kpi4:
                        st.metric(f"{team2} Win %", f"{t2_prob * 100:.1f}%")

                    # Probability bar chart
                    st.subheader("📊 Win Probability Breakdown")
                    prob_df = pd.DataFrame({
                        "Team":                [team1, team2],
                        "Win Probability (%)": [round(t1_prob * 100, 2), round(t2_prob * 100, 2)]
                    })
                    fig_prob = px.bar(
                        prob_df, x="Team", y="Win Probability (%)",
                        text="Win Probability (%)", color="Team",
                        color_discrete_sequence=["#2ecc71", "#3498db"]
                    )
                    fig_prob.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                    fig_prob.update_layout(yaxis_range=[0, 100], showlegend=False)
                    apply_chart_theme(fig_prob, height=320)
                    st.plotly_chart(fig_prob, use_container_width=True, theme=None)

                    # Predicted scores
                    st.subheader("🏏 Predicted Scores")
                    if t1_runs is not None and t2_runs is not None:
                        sc1, sc2 = st.columns(2)
                        with sc1:
                            st.metric(
                                f"{team1} Projected Runs",
                                f"{int(round(t1_runs))}",
                                help="Random Forest regression estimate from historical averages"
                            )
                        with sc2:
                            st.metric(
                                f"{team2} Projected Runs",
                                f"{int(round(t2_runs))}",
                                help="Random Forest regression estimate from historical averages"
                            )
                    else:
                        st.info("Score prediction unavailable — insufficient historical score data for this combination.")

                    st.caption(
                        "⚠️ These are probabilistic estimates based on historical ICC match data. "
                        "They are **not guaranteed match outcomes**."
                    )

                except ValueError as exc:
                    st.error(f"❌ {exc}")
                except Exception as exc:
                    st.error(f"❌ Prediction failed: {exc}")

        # ─────────────────────────────────────────────────────
        # MODEL PERFORMANCE METRICS PANEL
        # ─────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("📈 Model Performance Metrics")
        st.info(
            "ℹ️ **Historical metrics only** — measured on a held-out 20% test split of the "
            "international match dataset. These reflect past model performance and are "
            "**not guarantees of future prediction accuracy**."
        )

        wm = bundle.get("winner_metrics", {})
        sm = bundle.get("score_metrics", {})

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("🎯 Winner Accuracy",  f"{wm.get('accuracy', 0.0) * 100:.2f}%")
        with m2:
            st.metric("📐 Winner Precision", f"{wm.get('precision', 0.0) * 100:.2f}%")
        with m3:
            st.metric("🔁 Winner Recall",    f"{wm.get('recall', 0.0) * 100:.2f}%")
        with m4:
            st.metric("🏅 Winner F1 Score",  f"{wm.get('f1', 0.0) * 100:.2f}%")

        team1_r2 = sm.get("team1_r2") if isinstance(sm, dict) else None
        team2_r2 = sm.get("team2_r2") if isinstance(sm, dict) else None

        if team1_r2 is not None or team2_r2 is not None:
            sr1, sr2 = st.columns(2)
            with sr1:
                t1_txt = f"{team1_r2:.4f}" if team1_r2 is not None else "N/A"
                st.metric("📊 Team 1 Score R²", t1_txt)
            with sr2:
                t2_txt = f"{team2_r2:.4f}" if team2_r2 is not None else "N/A"
                st.metric("📊 Team 2 Score R²", t2_txt)
        else:
            st.caption("ℹ️ Score model R² metrics unavailable (insufficient score training data).")

        training_matches = bundle.get("training_matches", bundle.get("training_rows", 0))
        score_training_matches = bundle.get("score_training_matches", bundle.get("score_training_rows", 0))

        st.caption(
            f"**Training data:** {training_matches:,} international matches | "
            f"Score model: {score_training_matches:,} matches | "
            f"Teams: {len(bundle.get('teams', []))} | "
            f"Venues: {len(bundle.get('venues', []))} | "
            f"Formats: {', '.join(bundle.get('formats', []))}"
        )

    except Exception as exc:
        st.error(f"❌ Unable to load ML model: {exc}")
        st.info("Make sure `cricket.db` exists and contains data in the `ml_international_matches` table.")

    st.markdown("---")
    st.button("⬅ Back to Home", key="back_ml_bottom", on_click=navigate_page, args=("home",))

# ---------------- PLAYER PAGE ----------------
elif st.session_state.page == "players":

    st.markdown('<div class="title">📊 International Player Stats</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Verified International Career Statistics for Men\'s & Women\'s National Cricket Stars</div>', unsafe_allow_html=True)

    head_p1, head_p2 = st.columns([6, 1])
    with head_p1:
        st.caption("🌐 Official ICC International Player Database | Filter by Gender, Country, Format, and Playing Role")
    with head_p2:
        st.button("⬅ Back", key="back_players_top", on_click=navigate_page, args=("home",))

    # ---------- FILTERS SECTION ----------
    st.markdown("### 🔍 Filter International Players")
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        gender_opt = st.selectbox(
            "Gender",
            ["All", "Men's", "Women's"],
            key="p_gender_filter"
        )

    with f_col2:
        countries_available = sorted(list(set(p["country"] for p in INTERNATIONAL_PLAYERS_DATA.values())))
        country_opt = st.selectbox(
            "National Team",
            ["All"] + countries_available,
            key="p_country_filter"
        )

    with f_col3:
        role_opt = st.selectbox(
            "Player Role",
            ["All", "Batsman", "Bowler", "All-rounder", "Wicketkeeper"],
            key="p_role_filter"
        )

    with f_col4:
        search_kw = st.text_input("Search by Name", placeholder="e.g. Kohli, Perry...", key="p_search_kw")

    # Get dynamic matching players
    matching_players = get_filtered_players(
        gender=gender_opt,
        country=country_opt,
        role=role_opt,
        search_term=search_kw
    )

    if not matching_players:
        st.warning("⚠️ No international players found matching the selected filters. Try broadening your criteria.")
    else:
        st.markdown(f"**Found {len(matching_players)} verified international players:**")
        selected_player = st.selectbox(
            "Select International Player",
            matching_players,
            key="p_selected_player"
        )

        if selected_player:
            player_data = get_player_stats(selected_player)

            p_country = player_data.get("country", "")
            p_gender = player_data.get("gender", "Men's")
            p_role = player_data.get("role", "")
            p_teams = ", ".join(player_data.get("teams", []))
            p_flag = get_team_flag(p_country)

            gender_color = "#38bdf8" if p_gender == "Men's" else "#f472b6"

            # Player Profile Card
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%); border: 2px solid rgba(56, 189, 248, 0.35); border-radius: 16px; padding: 22px 28px; margin: 18px 0; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                    <div>
                        <div style="font-size: 32px; font-weight: 800; color: #f8fafc;">
                            <span style="font-size: 36px; margin-right: 8px;">{p_flag}</span> {selected_player}
                        </div>
                        <div style="color: #94a3b8; font-size: 15px; margin-top: 6px;">
                            Representing: <strong style="color: #e2e8f0;">{p_country}</strong> | Teams: <span style="color: #cbd5e1;">{p_teams}</span>
                        </div>
                    </div>
                    <div>
                        <span style="background: rgba(56, 189, 248, 0.15); color: {gender_color}; border: 1px solid {gender_color}; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 700; margin-right: 8px;">{p_gender} International</span>
                        <span style="background: rgba(14, 165, 233, 0.2); color: #38bdf8; border: 1px solid #38bdf8; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 700;">{p_role}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Calculate Career Aggregates
            bat_career = player_data.get("batting_career", {})
            bowl_career = player_data.get("bowling_career", {})

            total_matches = sum(f.get("matches", 0) for f in bat_career.values())
            total_runs = sum(f.get("runs", 0) for f in bat_career.values())
            total_100s = sum(f.get("100s", 0) for f in bat_career.values())
            total_50s = sum(f.get("50s", 0) for f in bat_career.values())
            total_wickets = sum(f.get("wickets", 0) for f in bowl_career.values())

            # Top KPI metrics
            kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
            with kpi_col1:
                st.metric("Total Matches", f"{total_matches}")
            with kpi_col2:
                st.metric("Total Runs", f"{total_runs:,}")
            with kpi_col3:
                st.metric("Centuries (100s)", f"{total_100s}")
            with kpi_col4:
                st.metric("Half-Centuries (50s)", f"{total_50s}")
            with kpi_col5:
                st.metric("Total Wickets", f"{total_wickets}")

            st.markdown("---")

            # Format-Wise Statistics Tabs
            tab_batting, tab_bowling, tab_viz, tab_api_search = st.tabs([
                "🏏 Batting Career Statistics",
                "🎯 Bowling Career Statistics",
                "📈 Career Charts & Comparisons",
                "📡 Live API Search"
            ])

            # ---------------- TAB 1: BATTING STATS ----------------
            with tab_batting:
                st.subheader("🏏 Batting Career by Format")
                st.caption(f"Official international batting records for {selected_player} across Test, ODI, and T20I matches.")

                bat_rows = []
                for fmt in ["Test", "ODI", "T20I"]:
                    if fmt in bat_career:
                        d = bat_career[fmt]
                        bat_rows.append({
                            "Format": fmt,
                            "Matches": d.get("matches", 0),
                            "Innings": d.get("innings", 0),
                            "Runs": d.get("runs", 0),
                            "Highest Score": d.get("highest", "-"),
                            "Average": d.get("average", 0.0),
                            "Strike Rate": d.get("strike_rate", 0.0),
                            "100s": d.get("100s", 0),
                            "50s": d.get("50s", 0)
                        })

                if bat_rows:
                    df_bat = pd.DataFrame(bat_rows)
                    st.dataframe(df_bat, use_container_width=True, hide_index=True)

                    # Highlight best format
                    best_runs_fmt = max(bat_rows, key=lambda x: x["Runs"])
                    b_col1, b_col2, b_col3 = st.columns(3)
                    with b_col1:
                        st.info(f"🏆 **Highest Runs Format**: {best_runs_fmt['Format']} ({best_runs_fmt['Runs']:,} runs)")
                    with b_col2:
                        best_avg_fmt = max(bat_rows, key=lambda x: x["Average"])
                        st.info(f"📊 **Best Average**: {best_avg_fmt['Average']} in {best_avg_fmt['Format']}")
                    with b_col3:
                        best_sr_fmt = max(bat_rows, key=lambda x: x["Strike Rate"])
                        st.info(f"⚡ **Highest Strike Rate**: {best_sr_fmt['Strike Rate']} in {best_sr_fmt['Format']}")

            # ---------------- TAB 2: BOWLING STATS ----------------
            with tab_bowling:
                st.subheader("🎯 Bowling Career by Format")
                st.caption(f"Official international bowling records for {selected_player} across Test, ODI, and T20I matches.")

                bowl_rows = []
                for fmt in ["Test", "ODI", "T20I"]:
                    if fmt in bowl_career:
                        d = bowl_career[fmt]
                        bowl_rows.append({
                            "Format": fmt,
                            "Wickets": d.get("wickets", 0),
                            "Best Bowling": d.get("best", "-"),
                            "Average": d.get("average", 0.0),
                            "Economy": d.get("economy", 0.0)
                        })

                if bowl_rows:
                    df_bowl = pd.DataFrame(bowl_rows)
                    st.dataframe(df_bowl, use_container_width=True, hide_index=True)

                    if total_wickets > 0:
                        bw_col1, bw_col2 = st.columns(2)
                        best_wkts_fmt = max(bowl_rows, key=lambda x: x["Wickets"])
                        with bw_col1:
                            st.success(f"🎯 **Most Wickets**: {best_wkts_fmt['Wickets']} wickets in {best_wkts_fmt['Format']}")
                        with bw_col2:
                            best_eco_fmt = min([b for b in bowl_rows if b["Economy"] > 0], key=lambda x: x["Economy"], default={"Format": "N/A", "Economy": 0})
                            st.success(f"🛡️ **Best Economy**: {best_eco_fmt['Economy']} in {best_eco_fmt['Format']}")
                    else:
                        st.info(f"ℹ️ {selected_player} is primarily a specialist batsman with limited bowling overs.")

            # ---------------- TAB 3: VISUAL COMPARISONS ----------------
            with tab_viz:
                st.subheader("📈 Format-by-Format Performance Analysis")

                if bat_rows:
                    fig_runs = px.bar(
                        df_bat,
                        x="Format",
                        y="Runs",
                        text="Runs",
                        color="Format",
                        title=f"{selected_player} - Career Runs across Formats",
                        color_discrete_map={"Test": "#0ea5e9", "ODI": "#06b6d4", "T20I": "#10b981"}
                    )
                    fig_runs.update_traces(textposition="outside")
                    apply_chart_theme(fig_runs, height=360)
                    st.plotly_chart(fig_runs, use_container_width=True, theme=None)

                    # Strike Rate vs Average comparison
                    fig_scatter = px.scatter(
                        df_bat,
                        x="Strike Rate",
                        y="Average",
                        size="Runs",
                        color="Format",
                        text="Format",
                        title=f"{selected_player} - Batting Average vs Strike Rate",
                        color_discrete_map={"Test": "#0ea5e9", "ODI": "#06b6d4", "T20I": "#10b981"}
                    )
                    fig_scatter.update_traces(textposition="top center", marker=dict(size=20))
                    apply_chart_theme(fig_scatter, height=360)
                    st.plotly_chart(fig_scatter, use_container_width=True, theme=None)

            # ---------------- TAB 4: LIVE API SEARCH ----------------
            with tab_api_search:
                st.subheader("📡 Cricbuzz RapidAPI Live Player Lookup")
                st.caption("Look up any active international player profile directly through Cricbuzz RapidAPI when your API key is configured.")

                api_key = get_rapidapi_key()
                if not api_key:
                    st.info("ℹ️ RapidAPI Key is not configured in `st.secrets` or environment. Add `RAPIDAPI_KEY` to enable live web lookup for unlisted players.")
                else:
                    live_query = st.text_input("Live Player Query", value=selected_player, key="live_api_plr_q")
                    if st.button("🔍 Search API", key="search_api_btn"):
                        with st.spinner("Querying Cricbuzz RapidAPI..."):
                            api_res = search_api_player(live_query)
                            if isinstance(api_res, dict) and api_res.get("quota_exceeded"):
                                st.warning(
                                    "⚠️ **Cricbuzz API quota exceeded.** "
                                    "Your RapidAPI monthly request limit has been reached. "
                                    "The local player database above is still fully available. "
                                    "Please try again after your quota resets (typically the 1st of next month)."
                                )
                            elif api_res:
                                st.success(f"Found {len(api_res)} player matches from Cricbuzz API:")
                                for plr in api_res:
                                    st.write(f"• **{plr.get('name')}** (ID: {plr.get('id')}) - Team: {plr.get('teamName', 'N/A')}")
                            else:
                                st.warning(f"No API results returned for '{live_query}'. Check the player name spelling or try another name.")

    st.markdown("---")
    st.button("⬅ Back to Home", key="back_players_bottom", on_click=navigate_page, args=("home",))

# ================== CRUD OPERATIONS PAGE ==================
elif st.session_state.page == "crud":

    st.title("⚙️ CRUD Operations - Database Management")

    st.markdown("""
    ### Manage Match Records
    Create, Read, Update, and Delete match records directly from your database.
    """)

    # CRUD Tabs
    crud_tab1, crud_tab2, crud_tab3, crud_tab4 = st.tabs(["➕ Create", "📖 Read", "✏️ Update", "🗑️ Delete"])

    # ==================== CREATE TAB ====================
    with crud_tab1:
        st.subheader("Add New Match")

        col1, col2 = st.columns(2)
        with col1:
            new_team1 = st.text_input("Team 1", placeholder="e.g., India")
            new_status = st.text_input("Status", placeholder="e.g., Day 2: Stumps - India trail by 50 runs")

        with col2:
            new_team2 = st.text_input("Team 2", placeholder="e.g., Australia")
            new_score = st.text_input("Score (optional)", placeholder="e.g., 250/5 vs 150/8")

        if st.button("➕ Add Match", key="create_btn"):
            if new_team1 and new_team2 and new_status:
                success, message = create_match(new_team1, new_team2, new_status, new_score if new_score else None)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
            else:
                st.warning("⚠️ Please fill in Team 1, Team 2, and Status fields")
    # ==================== READ TAB ====================
    with crud_tab2:
        st.subheader("View Matches")

        read_option = st.radio("View by:", ["All Matches", "By Team", "By Status"], horizontal=True)

        if read_option == "All Matches":
            success, matches = read_all_matches()
            if success and matches:
                df = pd.DataFrame(matches)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total: {len(matches)} matches in database")
            else:
                st.warning("No matches found")

        elif read_option == "By Team":
            success, teams = read_unique_teams()
            if success and teams:
                selected_team = st.selectbox("Select Team:", teams, key="read_team")
                success, matches = read_matches_by_team(selected_team)
                if success and matches:
                    df = pd.DataFrame(matches)
                    st.dataframe(df, use_container_width=True)
                    st.info(f"{selected_team} has played {len(matches)} matches")
                else:
                    st.warning("No matches found for this team")
            else:
                st.warning("No teams found in database")

        elif read_option == "By Status":
            success, statuses = read_unique_statuses()
            if success and statuses:
                selected_status = st.selectbox("Select Status:", statuses, key="read_status")
                success, matches = read_matches_by_status(selected_status)
                if success and matches:
                    df = pd.DataFrame(matches)
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Found {len(matches)} matches with this status")
                else:
                    st.warning("No matches found with this status")
            else:
                st.warning("No statuses found in database")

    # ==================== UPDATE TAB ====================
    with crud_tab3:
        st.subheader("Update Match Record")

        success, all_matches = read_all_matches()
        if success and all_matches:
            match_options = {f"ID {m['id']}: {m['team1']} vs {m['team2']}": m['id'] for m in all_matches}
            selected_match_display = st.selectbox("Select Match to Update:", list(match_options.keys()), key="update_select")
            selected_match_id = match_options[selected_match_display]

            success, match = read_match_by_id(selected_match_id)
            if success:
                st.info(f"Editing Match ID {selected_match_id}")

                update_option = st.radio("Update:", ["Full Update", "Score Only", "Status Only"], horizontal=True)

                if update_option == "Full Update":
                    col1, col2 = st.columns(2)
                    with col1:
                        upd_team1 = st.text_input("Team 1", value=match['team1'], key="upd_team1")
                        upd_status = st.text_input("Status", value=match['status'], key="upd_status")
                    with col2:
                        upd_team2 = st.text_input("Team 2", value=match['team2'], key="upd_team2")
                        upd_score = st.text_input("Score", value=match['score'] or "", key="upd_score")

                    if st.button("✏️ Update Full Record", key="update_full_btn"):
                        success, message = update_match(
                            selected_match_id,
                            upd_team1, upd_team2, upd_status,
                            upd_score if upd_score else None
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

                elif update_option == "Score Only":
                    new_score = st.text_input("New Score", value=match['score'] or "", key="score_only")
                    if st.button("✏️ Update Score", key="update_score_btn"):
                        success, message = update_match_score(selected_match_id, new_score)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

                elif update_option == "Status Only":
                    new_status = st.text_input("New Status", value=match['status'], key="status_only")
                    if st.button("✏️ Update Status", key="update_status_btn"):
                        success, message = update_match_status(selected_match_id, new_status)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        else:
            st.warning("No matches found to update")

    # ==================== DELETE TAB ====================
    with crud_tab4:
        st.subheader("Delete Match Record")
        st.warning("⚠️ Deletion is permanent and cannot be undone!")

        delete_option = st.radio("Delete:", ["Delete Single Match", "Delete by Status", "Delete All"], horizontal=True)

        if delete_option == "Delete Single Match":
            success, all_matches = read_all_matches()
            if success and all_matches:
                match_options = {f"ID {m['id']}: {m['team1']} vs {m['team2']}": m['id'] for m in all_matches}
                selected_match_display = st.selectbox("Select Match to Delete:", list(match_options.keys()), key="delete_select")
                selected_match_id = match_options[selected_match_display]

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Delete This Match", key="delete_single_btn"):
                        success, message = delete_match(selected_match_id)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                with col2:
                    st.info("This will remove only this match")
            else:
                st.warning("No matches to delete")

        elif delete_option == "Delete by Status":
            success, statuses = read_unique_statuses()
            if success and statuses:
                selected_status = st.selectbox("Select Status to Delete:", statuses, key="delete_status")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Delete All With This Status", key="delete_status_btn"):
                        success, message = delete_matches_by_status(selected_status)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                with col2:
                    st.info(f"Will delete all matches with status '{selected_status}'")
            else:
                st.warning("No statuses found")

        elif delete_option == "Delete All":
            st.error("⚠️ This will delete ALL matches from the database!")
            if st.checkbox("I understand the consequences", key="confirm_delete_all"):
                if st.button("🗑️ DELETE ALL MATCHES", key="delete_all_btn"):
                    success, message = delete_match(1)  # Try to delete, will handle differently
                    # Actually for delete all, use a safer approach
                    conn = sqlite3.connect("cricket.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) as count FROM matches")
                    total = cursor.fetchone()[0]

                    cursor.execute("DELETE FROM matches")
                    conn.commit()
                    conn.close()

                    st.error(f"⚠️ Deleted all {total} matches!")

    # ==================== DATABASE STATS ====================
    st.divider()
    st.subheader("📊 Database Statistics")

    success, stats = get_database_stats()
    if success:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Matches", stats['total_matches'])
        with col2:
            st.metric("Unique Teams", stats['unique_teams'])
        with col3:
            st.metric("Unique Statuses", stats['unique_statuses'])
        with col4:
            st.metric("Matches with Scores", stats['matches_with_scores'])

    st.button("⬅ Back", key="back_crud", on_click=navigate_page, args=("home",))

# ================== ENHANCED DATABASE MANAGEMENT PAGE ==================
elif st.session_state.page == "enhanced_db":

    st.title("📁 Enhanced Database Management")

    st.markdown("""
    ### Advanced Database Operations
    Manage teams, venues, players, and enhanced match records with proper relationships.
    """)

    # Enhanced DB Tabs
    enhanced_tab1, enhanced_tab2, enhanced_tab3, enhanced_tab4, enhanced_tab5 = st.tabs([
        "🏆 Teams", "📍 Venues", "👤 Players", "🎯 Enhanced Matches", "📊 Overview"
    ])

    # ==================== TEAMS TAB ====================
    with enhanced_tab1:
        st.subheader("Team Management")

        team_col1, team_col2 = st.columns(2)

        with team_col1:
            st.markdown("**Add New Team**")
            team_name = st.text_input("Team Name", key="team_name")
            team_short = st.text_input("Short Name", key="team_short")
            team_country = st.text_input("Country", key="team_country")
            team_captain = st.text_input("Captain", key="team_captain")
            team_coach = st.text_input("Coach", key="team_coach")

            if st.button("â Add Team", key="add_team_btn"):
                if team_name and team_short and team_country:
                    success, message = create_team(team_name, team_short, team_country, team_captain, team_coach)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Name, Short Name, and Country")

        with team_col2:
            st.markdown("**All Teams**")
            success, teams = read_all_teams()
            if success and teams:
                df = pd.DataFrame(teams)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total teams: {len(teams)}")
            else:
                st.warning("No teams found")

    # ==================== VENUES TAB ====================
    with enhanced_tab2:
        st.subheader("Venue Management")

        venue_col1, venue_col2 = st.columns(2)

        with venue_col1:
            st.markdown("**Add New Venue**")
            venue_name = st.text_input("Venue Name", key="venue_name")
            venue_city = st.text_input("City", key="venue_city")
            venue_country = st.text_input("Country", key="venue_country")
            venue_capacity = st.number_input("Capacity", min_value=0, key="venue_capacity")
            venue_pitch = st.selectbox("Pitch Type", ["Grass", "Turf", "Artificial"], key="venue_pitch")

            if st.button("â Add Venue", key="add_venue_btn"):
                if venue_name and venue_city and venue_country:
                    success, message = create_venue(venue_name, venue_city, venue_country, venue_capacity, venue_pitch)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Name, City, and Country")

        with venue_col2:
            st.markdown("**All Venues**")
            success, venues = read_all_venues()
            if success and venues:
                df = pd.DataFrame(venues)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total venues: {len(venues)}")
            else:
                st.warning("No venues found")

    # ==================== PLAYERS TAB ====================
    with enhanced_tab3:
        st.subheader("Player Management")

        player_col1, player_col2 = st.columns(2)

        with player_col1:
            st.markdown("**Add New Player**")

            # Get teams for dropdown
            success, teams = read_all_teams()
            team_options = {f"{t['name']} (ID: {t['id']})": t['id'] for t in teams} if success and teams else {}

            player_name = st.text_input("Player Name", key="player_name")
            player_full_name = st.text_input("Full Name", key="player_full_name")
            player_team = st.selectbox("Team", list(team_options.keys()), key="player_team") if team_options else None
            player_role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"], key="player_role")
            player_batting = st.selectbox("Batting Style", ["Right-handed", "Left-handed"], key="player_batting")
            player_bowling = st.selectbox("Bowling Style",
                ["Right-arm fast", "Left-arm fast", "Right-arm fast-medium", "Left-arm fast-medium",
                 "Right-arm medium", "Left-arm medium", "Right-arm off-break", "Left-arm off-break",
                 "Right-arm leg-break", "Left-arm leg-break", "None"], key="player_bowling")
            player_dob = st.date_input("Date of Birth", key="player_dob")
            player_nationality = st.text_input("Nationality", key="player_nationality")

            if st.button("â Add Player", key="add_player_btn"):
                if player_name and player_team and player_role:
                    team_id = team_options[player_team]
                    success, message = create_player(
                        player_name, player_full_name, team_id, player_role,
                        player_batting, player_bowling if player_bowling != "None" else None,
                        str(player_dob), player_nationality
                    )
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Name, Team, and Role")

        with player_col2:
            st.markdown("**All Players**")
            success, players = read_all_players()
            if success and players:
                df = pd.DataFrame(players)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total players: {len(players)}")
            else:
                st.warning("No players found")

    # ==================== ENHANCED MATCHES TAB ====================
    with enhanced_tab4:
        st.subheader("Enhanced Match Management")

        match_col1, match_col2 = st.columns(2)

        with match_col1:
            st.markdown("**Add New Enhanced Match**")

            # Get series, teams, venues for dropdowns
            success_series, series_list = read_all_teams()  # Placeholder - need to implement series CRUD
            success_teams, teams = read_all_teams()
            success_venues, venues = read_all_venues()

            series_options = {f"Series {i+1}": i+1 for i in range(5)}  # Placeholder
            team_options = {f"{t['name']} (ID: {t['id']})": t['id'] for t in teams} if success_teams and teams else {}
            venue_options = {f"{v['name']} (ID: {v['id']})": v['id'] for v in venues} if success_venues and venues else {}

            match_series = st.selectbox("Series", list(series_options.keys()), key="match_series") if series_options else None
            match_team1 = st.selectbox("Team 1", list(team_options.keys()), key="match_team1") if team_options else None
            match_team2 = st.selectbox("Team 2", list(team_options.keys()), key="match_team2") if team_options else None
            match_venue = st.selectbox("Venue", list(venue_options.keys()), key="match_venue") if venue_options else None
            match_date = st.date_input("Match Date", key="match_date")
            match_time = st.time_input("Match Time", key="match_time")
            match_status = st.text_input("Status", key="match_status")

            if st.button("â Add Enhanced Match", key="add_enhanced_match_btn"):
                if match_team1 and match_team2 and match_status:
                    series_id = series_options[match_series] if match_series else None
                    team1_id = team_options[match_team1]
                    team2_id = team_options[match_team2]
                    venue_id = venue_options[match_venue] if match_venue else None

                    success, message = create_enhanced_match(
                        series_id, team1_id, team2_id, venue_id,
                        str(match_date), str(match_time), match_status
                    )
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Team 1, Team 2, and Status")

        with match_col2:
            st.markdown("**Enhanced Matches**")
            success, matches = read_all_enhanced_matches()
            if success and matches:
                df = pd.DataFrame(matches)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total enhanced matches: {len(matches)}")
            else:
                st.warning("No enhanced matches found")

    # ==================== OVERVIEW TAB ====================
    with enhanced_tab5:
        st.subheader("Database Overview")

        # Get stats for all tables
        try:
            conn = sqlite3.connect("cricket.db")
            cursor = conn.cursor()

            stats = {}

            # Count records in each table
            tables = ['teams', 'venues', 'players', 'matches_enhanced', 'matches']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = cursor.fetchone()[0]
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Teams", stats.get('teams', 0))
                st.metric("Venues", stats.get('venues', 0))
                st.metric("Players", stats.get('players', 0))

            with col2:
                st.metric("Enhanced Matches", stats.get('matches_enhanced', 0))
                st.metric("Legacy Matches", stats.get('matches', 0))

            with col3:
                total_records = sum(stats.values())
                st.metric("Total Records", total_records)
                st.metric("Database Tables", len(tables))

            # Show table relationships
            st.markdown("### Database Schema")
            st.markdown("""
            ```
            teams (id, name, short_name, country, captain, coach)
            âââ venues (id, name, city, country, capacity, pitch_type)
            âââ players (id, name, full_name, team_idâteams.id, role, ...)
            âââ matches_enhanced (id, series_id, team1_idâteams.id, team2_idâteams.id, venue_idâvenues.id, ...)
                âââ scorecards (match_idâmatches_enhanced.id, team_idâteams.id, ...)
                âââ player_performance (match_idâmatches_enhanced.id, player_idâplayers.id, ...)
            ```
            """)

        except Exception as e:
            st.error(f"Error loading database overview: {str(e)}")

    st.button("â¬ Back", key="back_enhanced", on_click=navigate_page, args=("home",))

# ================== ENHANCED DATABASE MANAGEMENT PAGE ==================
elif st.session_state.page == "enhanced_db":

    st.title("ðï¸ Enhanced Database Management")

    st.markdown("""
    ### Advanced Database Operations
    Manage teams, venues, players, and enhanced match records with proper relationships.
    """)

    # Enhanced DB Tabs
    enhanced_tab1, enhanced_tab2, enhanced_tab3, enhanced_tab4, enhanced_tab5 = st.tabs([
        "ð Teams", "ðï¸ Venues", "ð¥ Players", "ð¯ Enhanced Matches", "ð Overview"
    ])

    # ==================== TEAMS TAB ====================
    with enhanced_tab1:
        st.subheader("Team Management")

        team_col1, team_col2 = st.columns(2)

        with team_col1:
            st.markdown("**Add New Team**")
            team_name = st.text_input("Team Name", key="team_name")
            team_short = st.text_input("Short Name", key="team_short")
            team_country = st.text_input("Country", key="team_country")
            team_captain = st.text_input("Captain", key="team_captain")
            team_coach = st.text_input("Coach", key="team_coach")

            if st.button("â Add Team", key="add_team_btn"):
                if team_name and team_short and team_country:
                    success, message = create_team(team_name, team_short, team_country, team_captain, team_coach)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Name, Short Name, and Country")

        with team_col2:
            st.markdown("**All Teams**")
            success, teams = read_all_teams()
            if success and teams:
                df = pd.DataFrame(teams)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total teams: {len(teams)}")
            else:
                st.warning("No teams found")

    # ==================== VENUES TAB ====================
    with enhanced_tab2:
        st.subheader("Venue Management")

        venue_col1, venue_col2 = st.columns(2)

        with venue_col1:
            st.markdown("**Add New Venue**")
            venue_name = st.text_input("Venue Name", key="venue_name")
            venue_city = st.text_input("City", key="venue_city")
            venue_country = st.text_input("Country", key="venue_country")
            venue_capacity = st.number_input("Capacity", min_value=0, key="venue_capacity")
            venue_pitch = st.selectbox("Pitch Type", ["Grass", "Turf", "Artificial"], key="venue_pitch")

            if st.button("â Add Venue", key="add_venue_btn"):
                if venue_name and venue_city and venue_country:
                    success, message = create_venue(venue_name, venue_city, venue_country, venue_capacity, venue_pitch)
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Name, City, and Country")

        with venue_col2:
            st.markdown("**All Venues**")
            success, venues = read_all_venues()
            if success and venues:
                df = pd.DataFrame(venues)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total venues: {len(venues)}")
            else:
                st.warning("No venues found")

    # ==================== PLAYERS TAB ====================
    with enhanced_tab3:
        st.subheader("Player Management")

        player_col1, player_col2 = st.columns(2)

        with player_col1:
            st.markdown("**Add New Player**")

            # Get teams for dropdown
            success, teams = read_all_teams()
            team_options = {f"{t['name']} (ID: {t['id']})": t['id'] for t in teams} if success and teams else {}

            player_name = st.text_input("Player Name", key="player_name")
            player_full_name = st.text_input("Full Name", key="player_full_name")
            player_team = st.selectbox("Team", list(team_options.keys()), key="player_team") if team_options else None
            player_role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"], key="player_role")
            player_batting = st.selectbox("Batting Style", ["Right-handed", "Left-handed"], key="player_batting")
            player_bowling = st.selectbox("Bowling Style",
                ["Right-arm fast", "Left-arm fast", "Right-arm fast-medium", "Left-arm fast-medium",
                 "Right-arm medium", "Left-arm medium", "Right-arm off-break", "Left-arm off-break",
                 "Right-arm leg-break", "Left-arm leg-break", "None"], key="player_bowling")
            player_dob = st.date_input("Date of Birth", key="player_dob")
            player_nationality = st.text_input("Nationality", key="player_nationality")

            if st.button("â Add Player", key="add_player_btn"):
                if player_name and player_team and player_role:
                    team_id = team_options[player_team]
                    success, message = create_player(
                        player_name, player_full_name, team_id, player_role,
                        player_batting, player_bowling if player_bowling != "None" else None,
                        str(player_dob), player_nationality
                    )
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Name, Team, and Role")

        with player_col2:
            st.markdown("**All Players**")
            success, players = read_all_players()
            if success and players:
                df = pd.DataFrame(players)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total players: {len(players)}")
            else:
                st.warning("No players found")

    # ==================== ENHANCED MATCHES TAB ====================
    with enhanced_tab4:
        st.subheader("Enhanced Match Management")

        match_col1, match_col2 = st.columns(2)

        with match_col1:
            st.markdown("**Add New Enhanced Match**")

            # Get series, teams, venues for dropdowns
            success_series, series_list = read_all_teams()  # Placeholder - need to implement series CRUD
            success_teams, teams = read_all_teams()
            success_venues, venues = read_all_venues()

            series_options = {f"Series {i+1}": i+1 for i in range(5)}  # Placeholder
            team_options = {f"{t['name']} (ID: {t['id']})": t['id'] for t in teams} if success_teams and teams else {}
            venue_options = {f"{v['name']} (ID: {v['id']})": v['id'] for v in venues} if success_venues and venues else {}

            match_series = st.selectbox("Series", list(series_options.keys()), key="match_series") if series_options else None
            match_team1 = st.selectbox("Team 1", list(team_options.keys()), key="match_team1") if team_options else None
            match_team2 = st.selectbox("Team 2", list(team_options.keys()), key="match_team2") if team_options else None
            match_venue = st.selectbox("Venue", list(venue_options.keys()), key="match_venue") if venue_options else None
            match_date = st.date_input("Match Date", key="match_date")
            match_time = st.time_input("Match Time", key="match_time")
            match_status = st.text_input("Status", key="match_status")

            if st.button("â Add Enhanced Match", key="add_enhanced_match_btn"):
                if match_team1 and match_team2 and match_status:
                    series_id = series_options[match_series] if match_series else None
                    team1_id = team_options[match_team1]
                    team2_id = team_options[match_team2]
                    venue_id = venue_options[match_venue] if match_venue else None

                    success, message = create_enhanced_match(
                        series_id, team1_id, team2_id, venue_id,
                        str(match_date), str(match_time), match_status
                    )
                    if success:
                        st.success(message)
                        st.balloons()
                    else:
                        st.error(message)
                else:
                    st.warning("â ï¸ Please fill in Team 1, Team 2, and Status")

        with match_col2:
            st.markdown("**Enhanced Matches**")
            success, matches = read_all_enhanced_matches()
            if success and matches:
                df = pd.DataFrame(matches)
                st.dataframe(df, use_container_width=True)
                st.info(f"Total enhanced matches: {len(matches)}")
            else:
                st.warning("No enhanced matches found")

    # ==================== OVERVIEW TAB ====================
    with enhanced_tab5:
        st.subheader("Database Overview")

        # Get stats for all tables
        try:
            conn = sqlite3.connect("cricket.db")
            cursor = conn.cursor()

            stats = {}

            # Count records in each table
            tables = ['teams', 'venues', 'players', 'matches_enhanced', 'matches']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = cursor.fetchone()['count']

            conn.close()

            # Display stats
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Teams", stats.get('teams', 0))
                st.metric("Venues", stats.get('venues', 0))
                st.metric("Players", stats.get('players', 0))

            with col2:
                st.metric("Enhanced Matches", stats.get('matches_enhanced', 0))
                st.metric("Legacy Matches", stats.get('matches', 0))

            with col3:
                total_records = sum(stats.values())
                st.metric("Total Records", total_records)
                st.metric("Database Tables", len(tables))

            # Show table relationships
            st.markdown("### Database Schema")
            st.markdown("""
            ```
            teams (id, name, short_name, country, captain, coach)
            âââ venues (id, name, city, country, capacity, pitch_type)
            âââ players (id, name, full_name, team_idâteams.id, role, ...)
            âââ matches_enhanced (id, series_id, team1_idâteams.id, team2_idâteams.id, venue_idâvenues.id, ...)
                âââ scorecards (match_idâmatches_enhanced.id, team_idâteams.id, ...)
                âââ player_performance (match_idâmatches_enhanced.id, player_idâplayers.id, ...)
            ```
            """)

        except Exception as e:
            st.error(f"Error loading database overview: {str(e)}")

    st.button("â¬ Back", key="back_enhanced", on_click=navigate_page, args=("home",))


# ================== DATA VISUALIZATIONS PAGE ==================
elif st.session_state.page == "visualizations":

    st.title("📈 Data Visualizations")
    st.markdown("### Interactive Charts and Analytics Dashboard")

    try:
        # Get database data
        conn = sqlite3.connect("cricket.db")
        cursor = conn.cursor()

        # Tab layout
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["🎯 Match Statistics", "👥 Player Analytics", "🏟️ Venue Analysis"])

        # ==================== MATCH STATISTICS ====================
        with viz_tab1:
            col1, col2 = st.columns(2)

            with col1:
                # Matches by Status
                st.subheader("Matches by Status")
                cursor.execute("""
                    SELECT status, COUNT(*) as count
                    FROM matches
                    GROUP BY status
                """)
                data = cursor.fetchall()

                if data:
                    status_names = [row[0] if row[0] else "Unknown" for row in data]
                    status_counts = [row[1] for row in data]

                    fig = go.Figure(data=[go.Pie(
                        labels=status_names,
                        values=status_counts,
                        marker=dict(colors=['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#8b5cf6'])
                    )])
                    apply_chart_theme(fig)
                    st.plotly_chart(fig, use_container_width=True, theme=None)

            with col2:
                # Team Performance (Most Matches)
                st.subheader("Teams by Match Count")
                cursor.execute("""
                    SELECT team1, COUNT(*) as count
                    FROM matches
                    GROUP BY team1
                    ORDER BY count DESC
                    LIMIT 8
                """)
                data = cursor.fetchall()

                if data:
                    teams = [row[0] for row in data]
                    counts = [row[1] for row in data]

                    fig = go.Figure(data=[go.Bar(
                        x=teams,
                        y=counts,
                        marker=dict(color=['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#8b5cf6', '#ec4899', '#f59e0b', '#ef4444'])
                    )])
                    fig.update_layout(
                        xaxis_title="Team",
                        yaxis_title="Matches Played"
                    )
                    apply_chart_theme(fig)
                    st.plotly_chart(fig, use_container_width=True, theme=None)

            # Total matches metric
            st.divider()
            col_m1, col_m2, col_m3 = st.columns(3)

            cursor.execute("SELECT COUNT(*) FROM matches")
            total_matches = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT team1) FROM matches")
            unique_teams = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT status) FROM matches WHERE status IS NOT NULL")
            unique_statuses = cursor.fetchone()[0]

            with col_m1:
                st.metric("📊 Total Matches", total_matches)
            with col_m2:
                st.metric("🏆 Unique Teams", unique_teams)
            with col_m3:
                st.metric("📋 Match Statuses", unique_statuses)

        # ==================== PLAYER ANALYTICS ====================
        with viz_tab2:
            col1, col2 = st.columns(2)

            with col1:
                # Players by Role
                st.subheader("Players by Role Distribution")
                cursor.execute("""
                    SELECT role, COUNT(*) as count
                    FROM players
                    GROUP BY role
                """)
                data = cursor.fetchall()

                if data:
                    roles = [row[0] for row in data]
                    role_counts = [row[1] for row in data]

                    fig = go.Figure(data=[go.Bar(
                        x=roles,
                        y=role_counts,
                        marker=dict(color=['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981'])
                    )])
                    fig.update_layout(
                        xaxis_title="Player Role",
                        yaxis_title="Count"
                    )
                    apply_chart_theme(fig)
                    st.plotly_chart(fig, use_container_width=True, theme=None)

            with col2:
                # Players by Nationality
                st.subheader("Top 10 Countries by Player Count")
                cursor.execute("""
                    SELECT nationality, COUNT(*) as count
                    FROM players
                    WHERE nationality IS NOT NULL
                    GROUP BY nationality
                    ORDER BY count DESC
                    LIMIT 10
                """)
                data = cursor.fetchall()

                if data:
                    countries = [row[0] for row in data]
                    counts = [row[1] for row in data]

                    fig = go.Figure(data=[go.Scatter(
                        x=countries,
                        y=counts,
                        mode='markers+lines',
                        marker=dict(size=12, color='#0ea5e9'),
                        line=dict(color='#06b6d4')
                    )])
                    fig.update_layout(
                        xaxis_title="Country",
                        yaxis_title="Players Count"
                    )
                    apply_chart_theme(fig)
                    st.plotly_chart(fig, use_container_width=True, theme=None)

            # Player metrics
            st.divider()
            col_p1, col_p2, col_p3 = st.columns(3)

            cursor.execute("SELECT COUNT(*) FROM players")
            total_players = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT team_id) FROM players WHERE team_id IS NOT NULL")
            players_with_team = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT nationality) FROM players WHERE nationality IS NOT NULL")
            nationalities = cursor.fetchone()[0]

            with col_p1:
                st.metric("👥 Total Players", total_players)
            with col_p2:
                st.metric("🎯 Teams Assigned", players_with_team)
            with col_p3:
                st.metric("🌍 Nationalities", nationalities)

        # ==================== VENUE ANALYSIS ====================
        with viz_tab3:
            col1, col2 = st.columns(2)

            with col1:
                # Venues by Pitch Type
                st.subheader("Venues by Pitch Type")
                cursor.execute("""
                    SELECT pitch_type, COUNT(*) as count
                    FROM venues
                    GROUP BY pitch_type
                """)
                data = cursor.fetchall()

                if data:
                    pitch_types = [row[0] if row[0] else "Unknown" for row in data]
                    counts = [row[1] for row in data]

                    fig = go.Figure(data=[go.Pie(
                        labels=pitch_types,
                        values=counts,
                        marker=dict(colors=['#0ea5e9', '#06b6d4', '#14b8a6'])
                    )])
                    apply_chart_theme(fig)
                    st.plotly_chart(fig, use_container_width=True, theme=None)

            with col2:
                # Venue Capacity Analysis
                st.subheader("Venues by Capacity")
                cursor.execute("""
                    SELECT name, capacity
                    FROM venues
                    WHERE capacity > 0
                    ORDER BY capacity DESC
                    LIMIT 10
                """)
                data = cursor.fetchall()

                if data:
                    venues = [row[0] for row in data]
                    capacities = [row[1] for row in data]

                    fig = go.Figure(data=[go.Bar(
                        y=venues,
                        x=capacities,
                        orientation='h',
                        marker=dict(color=['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#8b5cf6', '#ec4899', '#f59e0b', '#ef4444', '#f97316', '#a855f7'])
                    )])
                    fig.update_layout(
                        xaxis_title="Capacity",
                        yaxis_title="Venue"
                    )
                    apply_chart_theme(fig)
                    st.plotly_chart(fig, use_container_width=True, theme=None)

            # Venue metrics
            st.divider()
            col_v1, col_v2, col_v3 = st.columns(3)

            cursor.execute("SELECT COUNT(*) FROM venues")
            total_venues = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT country) FROM venues")
            countries = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(capacity) FROM venues WHERE capacity > 0")
            avg_capacity_result = cursor.fetchone()[0]
            avg_capacity = int(avg_capacity_result) if avg_capacity_result else 0

            with col_v1:
                st.metric("🏟️ Total Venues", total_venues)
            with col_v2:
                st.metric("🌍 Countries", countries)
            with col_v3:
                st.metric("📊 Avg Capacity", f"{avg_capacity:,}")

        conn.close()

    except Exception as e:
        st.error(f"Error loading visualizations: {str(e)}")
        st.info("Make sure you have data in the database tables.")

    st.divider()
    st.button("⬅ Back", key="back_viz", on_click=navigate_page, args=("home",))
