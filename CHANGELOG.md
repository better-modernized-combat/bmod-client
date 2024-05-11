# Changelog

## 0.0.10
- Possible fix for the crash documented in Issue #91.
- Adjust distance between players where NPC spawns will start to scale.
- Increase distances at which players are visible to one another.
- Fixes for elite and ace NPC behaviours.

## 0.0.9
- Added some new points of interest you can find via interacting with the hackable satellites
- Fixed NPC loadouts and cargo to be closer to what's intended
- Allowed NPCs to flee when taking too much damage
- Removed WIP weapons and ships from being for sale
- Added a few more static ships and objects throughout Colorado
- Made Rocket Pods a Small Missile instead of a Medium, increased their max ammo.
- Fixed Xenos Independence freighter ships from being faster than intended
- Introduced Mule transports to the Xenos's spawns
- New treasure loot dropping system, currently using a range of placeholder items
- Made the rearview camera a wider FOV to be more useful
- Allowed NPCs to switch targets in a dogfight more organically
- Big changes to the spawns of all NPCs across all areas of Colorado
- Buffed the damage of LRMs
- Increased the value of Xenos bounty tokens
- Added enhanced variants of basic gear to Pueblo Station, sold at exorbitant prices
- Added above enhanced variants to elite NPCs who will also drop them rarely on death
- Added the Rhino freighter for sale to players on Pueblo Station along with its own category of gear seperate from fighters (Fleet equipment)
- Added and adjusted Colorado dust cloud nebulas for the various fields
- Fixed a bug that was causing autocannons and missiles to not do their listed damage against shields
- Fixed a bug that was causing UGBs and Rockets from working properly in MP
- Removed some superfluous commodities for sale from Colorado bases for now
- Many other fixes to various things

## 0.0.8
- Objectives: Multiplayer now features satellites that can be hacked to reveal points of interest
- Experimental changes to the handling of player-flyable ships
- Adjusted a number of visual and audio effects
- Reduced the rock density of the Cheyenne Asteroid Field
- Numerous adjustments to Rookie NPC flight AI
- A better basic economy for Colorado, with across-the-board changes to prices and commodities, which now feature volume as a balancing factor
- Cheyenne and Silverton Miner solars are now a bit more interesting
- General adjustments around Colorado
- Implement placeholder 'treasure' loot
- Rejig internal names for wrecks to prevent some strange bugs
- Numerous assorted bug fixes

## 0.0.7
- Reimplement basic commodities with modifiable counterparts
- Set up a very basic group of producers and consumers within Colorado
- Give pilots, tokens and dogtags a base sell price and set up points they can be sold at

## 0.0.6
- Resize L, M and S laser models to fit properly onto fighter hardpoints
- Implement placeholder satellite solars in Colorado
- Implement vignette zones in Colorado in preparation for hacking and objective system
- Implement hacking VFX and fuses in preparation for hacking and objective system
- Implement hacking response loadouts for `li_n_grp` and `fc_x_grp`
- Adjust keymap.ini so defaults for switching weapon groups and turning in turret mode are present

## 0.0.5
- Lootprops now generates automatically any required entries coming from the variant gun/aux script
- INI validation script properly outputs mistakes
- Added new voucher and dog tag icons
- Cleaned up infocards.frc a little
- Phantom -> Paladin
- Scrambled Signal is back
- Bulk-renamed pilot commodities across inis so they have consistent naming
- Fixed a couple thousand paths with incorrect casing

## 0.0.4
- Adjustments to 'Fleet' equipment. Classes for freighters now use XL Missile, XL Ballistic, XL Energy, PD Turret and XL Support hardpoints
- Replace several placeholder infocards with complete ones
- Restore icons for many auxiliary weapons that previously didn't have any
- Ensure the bases in Colorado have XL equipment for sale
- Properly Implement and Balance the Paladin

## 0.0.3
- Add tradelane traffic to Colorado
- Add Navy, Police, DSE and Ageira NPC ambient zones
- Add Generic 'coverage' zone for the entire system so patrols are able to happen in empty space occasionally
- Fix missing VFX and SFX for a number of weapons
- Adjust handling and health values on NPC transports
- Add new NPC-locked base: 'Galileo Gate Construction Site'

## 0.0.2
- Add basic equipment back to bases in Colorado

## 0.0.1
- Alpha pre-release for v0.1 "Goose".
