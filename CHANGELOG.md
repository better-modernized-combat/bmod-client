# Changelog

## 0.0.24
- Deploy critical fix for an issue that caused a crash when the game Window lost focus.
- Enable more than 3 ships to be offered at a shipdealer, remove ships for sale at Pueblo station.
- Implement improved Wheel Scroll QOL patch from Adoxa

## 0.0.23
- Implement patch notes system for the main menu.
- Implement Laz's Raid UI.
- Implement Laz's Crash Walker module. This will handle instances where the game crashes to desktop and provide feedback where a known crashes occurs.
- Implement optional autoconnect plugin.

## 0.0.22
- Implemented an all-new fully modelled Xenos weapons platform made for ambushes in asteroid fields, the Trapdoor. Currently has test spawns in the field south of the dev station (<3 IrateRedKite)
- Added a new Navy checkpoint with a static Frigate and some weapons platforms between Denver and Alamosa field. WIP, not final yet (Beagle)
- Added a new Triggers Terminal to this Navy outpost. It provides static Xenos targets to attack in Alamosa field. WIP, currently uses existing content from the Cheyenne DSE Terminal as placeholders (Beagle) 
- Behind the scenes cleanup and optimizations (<3 IrateRedKite)
- Brand new visual hardpoints with better detail and relative sizing to suit our weapon class system (<3 IrateRedKite)
- New and improved hitboxing and shields for the Civilian fighter line: Hawk, Falcon, Eagle (<3 Haste)
- Hawk LF and Eagle VHF have been resized - the Hawk has become a little smaller, the Eagle a little larger. If these changes playtest well, we'll be aiming to standardize these kinds of size differences between all fighter classes in the future (<3 IrateRedKite)

## 0.0.21
- Fixed a breaking issue that caused the game to crash when launching into space in Colorado (#197). Due to the root cause of this, we have had to disable our XML to UTF pipeline for the time being. Developers may wish to clone a fresh copy of the repository before proceeding with any work following this release.
- Break the jumpgate at Kepler into even more pieces.
- Add new shield model variants for different shield types.

## 0.0.20
- Fixed an error related to docking ring costumes.
- Minor tweaks to the weapon generation script.
- Fixed excess contrails on some NPC Anglers.
- Remove unwanted spin value from planets.
- New explosion VFX for the Mule pirate freighter.
- Fix #189, where dealers were sometimes blocked by a rumor dialog on Prison Liner Tamms
- Add some interesting scenery to the Galileo Gate Construction Site, Pueblo Station and around Prison Liner Tamms.
  
## 0.0.19
- New explosion VFX for freighter-sized ships.
- New explosion VFX for the Liberty fighter line.
- New explosion VFX for the Junker fighter line.
- Fixes to the build script to ensure an error-free lootprops.ini file.
- Clean up some unused prototype VFX.

## 0.0.18
- Various text fixes.
- Minor audio and infocard content additions.
- Experimental NPC state graphs added.

## 0.0.17
- Fix for a crash that occurred when destroying NPCs in Copperton
- Create 'Aggressive', 'Cowardly' and 'Standard' pilots.
- Some internal adjustments made to unused systems in preparation for modification with LancerEdit

## 0.0.16
- Increased tradelane regeneration time when intercepted from 30s to 90s.
- Deployed a fix for a persistent crash in single-player that occurred when using tradelanes (#94).
- Fixed visibility of some fields.
- Add some additional static points of interest to Colorado.

## 0.0.15
- Fixed the missile range formula and changed 'Maximum Range' to 'Approximate Range' to better convey what the numbers in this field actually represent.
- Fixed a server crash that occurred when destroying a particular NPC Orca type.
- Fixed burst fire behaviour courtesy of adjustments made to our plugins by @Volken.

## 0.0.14
- Xenos NPC accuracy was too high, it's been lowered to more reasonable levels now so you should be able to survive in more situations like when you're outnumbered.
- Added a new shipline modelled by our new collaborator, McDyson! Meet the Manta, Angler and Orca fighters in the hands of Xenos NPCs, or buy them on the Xenos's Ouray station. They're slightly flimsier in some ways than the civilian Falcon line, but they have a more flexible hardpoint setup.
- Implemented a full new system of discovering dynamic events and points of interest by interacting with (and potentially hacking) useable terminals found in space across Colorado, thanks to IrateRedKite's very hard work. These terminals, tagged with [USE] at the start of their name, can be interacted with by selecting them and typing `/terminal use` or `/terminal hack`, for legal and illegal options respectively. These interactions give the player information on interesting things, events and opportunities to make a profit. Legal use cost credits, while hacking may trigger consequences from the terminal's owning faction. Type '/terminal show' to review the information you've recieved.
- For this first implementation, there is only one active terminal to interact with, a DSE mineral scanning radar that can be found between Planet Denver and the Cheyenne asteroid field. It can provide information on profitable mining, salvage and other opportunities it detects through geological analysis. Many more terminals and events will be added soon that cover many different types of gameplay, including trading, exploration, bounty hunting, research, and combat.
- Made ores and gems sell for better prices.
- Added a new Support Turret tool, a mining beam intended for CSVs and Rhinos to use in cutting up ore-carrying rocks and salvageable wrecks at point blank range. For sale on Denver and Pueblo.
- Made it so [+] gear doesn't cost absurd amounts to repair anymore, this was unintended.
- Added new [+] gear for sale on Pueblo, inculding enhanced variants of Autocannons, MGs, Lasers and PPCs.
- Ammo for [+] weaponry added to all stores for convenience.
- Lowered the sizes of the Mule group spawns a bit.
- NPCs should spam less Cruise Disruptors at you, reducing their obnoxiousness.
- Repair gun range was doubled.
- Tweaks to Xenos weapons loadouts, including less lasers across the board for all pilots except for Elites.
- Light Fighters had their agility nerfed somewhat.
- VHFs recieved a small buff to their top speed.
- Added a roundabout way to start a pirate character, just shoot up the crates on the cargo depots outside Planet Denver until you're neutral with Xenos (and red with the Navy.)
- The Rhino has been resized and had it's shape and hardpoints adjusted slightly to better fit fleet-sized gear.
- New models for launched SRMs and LRMs that can properly be shot down with weapons fire. This is especially useful for Rhino players who can use point defense guns to protect themselves from these missiles.
- New models for some fighter auxilliary gear: Machine Guns, LRM pylons and SRM pylons should now have distinct models.
- Shields added to DSE Mining Ships and the Xenos Ludlow frigate.
- In addition, big upgrade to the Xenos's Ludlow frigate in general, as along with a new shield and a new model (Thanks McDyson!), it has a completely frigate-appropriate weapons loadout which provides massively increased lethality.
- Fixed problems with how destructible solars like the Ludlow frigate would respawn wrong and not drop loot. They should now blow up properly, only respawn on server restarts, and have their loot drop consistently when killed.
- First Torpedo implemented, the Skipper Light Torpedo, an L Missile weapon intended for hunting freighter sized targets. Sold on most bases in Colorado.
- Added bomber-style loadouts as an alternative spawn for Xenos VHFs. They can now spawn with PPCs and Torpedoes for hunting freighters.
- Adjusted buy and sell prices of commodities and etcetera across all bases in Colorado, including the addition of proper sell prices to Ouray base for pirate players.
- Changed the appearance and behaviour of any newly created MP characters from this point on - they will appear as anonymously helmeted and mute.
- Increased range at which Countermeasures can distract incoming missiles, and how long Wasp Cruise Disruptor missiles can fly for before self-destructing.
- Buffs to PPCs and Lasers, including fleet versions, to make them more effective and easier to use.
- Nerf to the AC/L's damage output, it was overperforming.
- Complete rework of the NAC/L; its slow-firing, huge damage behaviour was transferred to a new Fleet Medium Ballistic, the NAC/H, while the NAC/L is now a faster firing but lighter gun instead that provides high damage at closer ranges.
- Ballistic PD Turrets can now be bought on Pueblo.
- Tweaks to how Fleet LRMs and SRMs work. LRMs fire in a fixed high-arc from the launcher now, like arcing artillery. They both fire more missiles now, too.
- Fleet PPC now fires two projectiles instead of one, making it twice as powerful.
- New fleet-sized weapon, the Fleet Quad Autocannon, a Small Turret Ballistic gun that provides high damage at close range, perfect for enhancing your anti-fighter power on the Rhino.
- Area of effect increased for UGBs and Rocket Pods; they'll do splash damage in a wider range now.
- Reduced density of those little annoying micro-rocks in Colorado's asteroid fields. They threw your aim off a lot and were generally irritating at their previous density.
- Attempted to spread out the player formation in MP so players don't bang into each other on autopilot when formed up, unsure if the fix targeted the right formation, testing needed please!
- Fixed multibarrel weapons using the wrong amount of ammo.
- Fixed multiple crashes.
- Many general improvements.
- Known Issue: Objects that 'move around' on server restart do not currently have infocards.
- Known Issue: Some objects that 'move around' on restart or objects that are created in space when interacting with a terminal do not properly display their name infocard.
- Known Issue: Fire sounds play inconsistently when multiple multibarrel weapons are fired at once.
- Client instability when using tradelanes in singleplayer mode.


## 0.0.13
- Enhanced gear tweaked to fix an issue. Please note if you had any of the old enhanced gear marked with a [+] symobl on your ship before this update, you won't be able to log in to that character now! Players were warned to discard this gear prior to this update as a result.
- To be clear, now that this issue has been fixed, you are 100% clear to start buying and using enhanced gear marked with [+] as intended. Go ahead and have fun with it!
- New enhanced gear added to Pueblo: Countermeasure Dropper [+], Cruise Disruptor [+], Repair Mine [+], and [+] variants of the single SRM and LRM launchers as well as their pylon variants. More enhanced gear is soon to come.
- New enhanced blasters added for the other faction weapon lines, for sale on their appropriate bases.
- Rhino cruise spool-up SFX improved to match its slower rate.
- Tikas and Ludlow changed to fix a bug. They won't explode and disappear now at 0 HP, but instead will drop loot as they get close to that number. If you see loot pop out of them, you can consider them defeated. We'll add better effects to replace the satisfying exploding for defeating them in a later update.
- Fix the Rhino's cruise charge audio not matching the charge time.

## 0.0.12
- CSV added! This is a Heavy Fighter Plus-sized ship that trades having lesser firepower and agility in exchange for Support hardpoints and a much larger cargo hold. This means it's intended to be a support fighter and small transport, capable of repairing allies, carrying larger amounts of loot, and being used for profitable trade runs between Colorado's bases. It's currently available for sale on Pueblo station.
- Buffed the profitability of the current Colorado trade runs - their profit margins were razor thin before and were only designed to be worth doing on the Rhino freighter with its 500 cargo hold. That's been changed now so that the new CSV can make profitable runs with its 180 cargo. Note that while some goods can make you a hefty profit now, the most lucrative cargo also requires the biggest up-front investment to buy it - which means if you lose that cargo, you'll be taking a big hit.

## 0.0.11
- Fix for edge-case crash where NPCs would tractor loot that they wouldn't usually have.
- Some minor internal fixes

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
