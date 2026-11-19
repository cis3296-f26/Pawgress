# Manual tests

The pytest suite covers the logic, but it can't tell us if the commands actually show up and behave in Discord. Run through these in a test server after any big change. Use a fresh database (delete `data/database.db`) so the coin and pet checks start from zero.

| # | Steps | Expected |
|---|-------|----------|
| 1 | Start the bot with `py main.py` | Console prints "Logged in as ..." with no errors |
| 2 | Type `/` in the server | All Pawgress commands show up in the list |
| 3 | `/help` | Embed with General, Pet, Study, Store and User sections |
| 4 | `/pet_create` | "Your new pet has been created!" |
| 5 | `/pet_create` again | Says the server already has a pet and shows its name and type |
| 6 | `/pet_rename` with a new name | "Your pet is now named **name**!" |
| 7 | `/pet_change` and pick Cat | "You now have a **Cat**!" |
| 8 | `/user_balance` on a new account | "You have **0** coins", only you can see it |
| 9 | `/store_catalog` | Regular, Super and Mega with hunger and price, cheapest first |
| 10 | `/store_buy` Regular Food with 0 coins | "You don't have enough coins...", only you can see it |
| 11 | `/study_info` | Embed describing Pomodoro, 90-minute block and Freeflow |
| 12 | `/study_start` Freeflow, wait 4 minutes, `/study_stop` | "Timer stopped. Studied for 4 minutes." |
| 13 | `/user_balance` | 2 coins (1 coin per 2 minutes studied) |
| 14 | `/study_stop` with nothing running | "No timer to be stopped." |
| 15 | `/study_start` Pomodoro and leave it for 25 minutes | Bot pings you in the channel for a 5 minute break |
| 16 | Study long enough for 15+ coins, then `/store_buy` Regular Food | "... bought **Regular Food** for 15 coins!" and balance goes down by 15 |
| 17 | `/user_inventory` | Shows Regular Food with the right quantity |
| 18 | Try the pet and store commands in a DM with the bot | Discord won't allow them since they're server only |
| 19 | Have a second person run `/user_balance` and `/user_inventory` | Their coins and items are separate from yours |

## Known issues found while testing

- The README lists `/create_pet` and `/rename_pet` but the real commands are `/pet_create`, `/pet_rename` and `/pet_change`.
- `/study_info` footer tells you to use `/start` instead of `/study_start`.
- Mega costs 40 in the catalog but `/store_buy` charges 45.
- `/study_start` works without a pet but `/study_stop` says "Pet not found" so you can't stop it.
- Running `/study_start` twice leaves the first timer running in the background.

The last four have tests marked `xfail` in `tests/`. Once one gets fixed, that test will start passing and pytest will flag it, so just delete the `xfail` line.
