# Brackeys Game Design playlist source record

Playlist:
https://www.youtube.com/playlist?list=PLPV2KyIb3jR5kPzHBi90byfhPfPqaDW9s

This note preserves what the source material supports and separates it from the repository's agent-specific operating rules.

The skills under `src/super_mcp/game_repo_template/.agents/skills/` are adaptations. They are not transcripts.

## Playlist structure

A public course index for the playlist lists six lessons and 59 minutes of video:

1. "Basic Principles of Game Design" - 09:06
2. "Difficulty in Video Games - Game Design" - 12:09
3. "Keeping players Interested - Pacing in Game Design" - 11:37
4. "Storytelling in Video Games" - 07:57
5. "What makes Combat Fun?" - 05:38
6. "How to MAKE YOUR GAME LOOK GOOD!" - 13:02

Course index:
https://coursehive.io/courses/game-design-75

## Basic principles

Video:
https://www.youtube.com/watch?v=G8AT01tuyrk

The Brackeys description frames the lesson as breaking down the broad question of how to make good games.

An indexed teaching summary tied to this video describes these ideas:

- judge design against the intended player experience rather than universal rules;
- player, communication, and appeal as three pillars;
- the player needs purpose and agency;
- anticipation prepares the player for important events;
- game responses should meet learned or subconscious expectations;
- deliberately changed rules should remain consistent.

Indexed summary:
https://www.robloxdev.academy/

These ideas anchor `game-design-foundations`.

## Difficulty

Video:
https://www.youtube.com/watch?v=bxp4G-oJATM

The Brackeys description says the video explores how to balance difficulty and links further reading on dynamic difficulty adjustment.

An indexed note explicitly based on the topic summarizes:

- difficulty should be balanced for the target audience;
- difficulty should be fair;
- failure should be understandable enough to inform another attempt;
- consistent rules matter;
- complexity is not the same as difficulty;
- useful depth can come from a small rule set.

Secondary note:
https://ruk.si/notes/games/game-design-difficulty/

These ideas anchor `game-difficulty`. The skill adds repository policy such as tuning one dimension at a time and requiring actual play.

## Pacing

Video:
https://www.youtube.com/watch?v=ftiHgyFt72M

The Brackeys description says the video explores how pacing can keep players interested and links additional material on pacing, progression, and engagement.

The repository adapts that lens into explicit checks for intensity over time, recovery, learning cadence, novelty, repetition, and reward timing.

Those detailed checks are operational guidance. They should not be attributed as direct quotes from the video.

## Storytelling

Video:
https://www.youtube.com/watch?v=fQgmPJYUiqw

An indexed Brackeys archive describes the lesson as asking how to tell a story effectively in a video game and showing examples of games that do it well.

Archive:
https://archive.ventilaar.net/channel/UCYbK_tjZ2OrIZFBvU6CCMiA

The repository adapts that question into guidance around player role, story through play, environment, consequence, narrative/gameplay coherence, proportional lore, and pacing.

Those detailed workflow rules are an adaptation, not a transcript.

## Combat

Video:
https://www.youtube.com/watch?v=DjsFUOffakc

The Brackeys video description points directly to Mike Birkhead's article "What Makes Combat Fun?"

Article:
https://www.gamedeveloper.com/design/opinion-what-makes-combat-fun

The article's core model says combat benefits from multiple valid intentions and action sequences, then situational constraints from goals, environment, and opponents. It also stresses clarity so the player can perceive options and constraints while retaining room for discovery.

These ideas anchor `game-combat`.

## Visual presentation

Video:
https://www.youtube.com/watch?v=nvbQ9_bzx1k

The Brackeys description presents the video as simple techniques for making a game look good.

An indexed summary of the video emphasizes:

- composition;
- lighting;
- movement;
- color;
- directing player attention;
- strong presentation without requiring high-cost assets.

Indexed summary:
https://app.daily.dev/posts/ayzonnevl

These ideas anchor `game-visuals`. The repository adds explicit Blender-to-Godot asset iteration, gameplay-camera review, readability checks, and polish budgeting.

## Repository-specific additions

The following policies come from the game-development discussion that motivated ADR 0007, not from claims about the playlist:

- treat uncertain design as a hypothesis and cheap playable experiment;
- distinguish exploration, production, and maintenance;
- make one conceptual change before playtesting when practical;
- record observations before diagnoses;
- prefer engine features, data, and local code before new systems;
- do not generalize from one consumer;
- leave stable code alone without measured friction;
- spend quality according to player exposure and dependency cost;
- import Blender assets into the game early;
- maintain a living `GAME_DESIGN.md`;
- promote ideas only after evidence;
- stop when the requested behavior and current design question are verified.

Future edits should keep that distinction explicit.
