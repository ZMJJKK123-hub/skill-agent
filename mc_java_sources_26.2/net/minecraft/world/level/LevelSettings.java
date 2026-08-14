package net.minecraft.world.level;

import com.mojang.serialization.Codec;
import com.mojang.serialization.Dynamic;
import com.mojang.serialization.Lifecycle;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.Difficulty;
import net.minecraftforge.common.ForgeHooks;

public record LevelSettings(
   String levelName,
   GameType gameType,
   LevelSettings.DifficultySettings difficultySettings,
   boolean allowCommands,
   WorldDataConfiguration dataConfiguration,
   Lifecycle lifecycle
) {
   public LevelSettings(
      String levelName, GameType gameType, LevelSettings.DifficultySettings difficultySettings, boolean allowCommands, WorldDataConfiguration dataConfiguration
   ) {
      this(levelName, gameType, difficultySettings, allowCommands, dataConfiguration, Lifecycle.stable());
   }

   public static LevelSettings parse(Dynamic<?> input, WorldDataConfiguration loadConfig) {
      GameType gameType = GameType.byId(input.get("GameType").asInt(0));
      return new LevelSettings(
         input.get("LevelName").asString(""),
         gameType,
         input.get("difficulty_settings").read(LevelSettings.DifficultySettings.CODEC).result().orElse(LevelSettings.DifficultySettings.DEFAULT),
         input.get("allowCommands").asBoolean(gameType == GameType.CREATIVE),
         loadConfig,
         ForgeHooks.parseLifecycle(input.get("forgeLifecycle").asString("stable"))
      );
   }

   public LevelSettings withGameType(GameType gameType) {
      return new LevelSettings(this.levelName, gameType, this.difficultySettings, this.allowCommands, this.dataConfiguration, this.lifecycle);
   }

   public LevelSettings withAllowCommands(boolean allowCommands) {
      return new LevelSettings(this.levelName, this.gameType, this.difficultySettings, allowCommands, this.dataConfiguration);
   }

   public LevelSettings withDifficulty(Difficulty difficulty) {
      return new LevelSettings(
         this.levelName,
         this.gameType,
         new LevelSettings.DifficultySettings(difficulty, this.difficultySettings.hardcore(), this.difficultySettings.locked()),
         this.allowCommands,
         this.dataConfiguration,
         this.lifecycle
      );
   }

   public LevelSettings withDifficultyLock(boolean locked) {
      return new LevelSettings(
         this.levelName,
         this.gameType,
         new LevelSettings.DifficultySettings(this.difficultySettings.difficulty(), this.difficultySettings.hardcore(), locked),
         this.allowCommands,
         this.dataConfiguration,
         this.lifecycle
      );
   }

   public LevelSettings withDataConfiguration(WorldDataConfiguration dataConfiguration) {
      return new LevelSettings(this.levelName, this.gameType, this.difficultySettings, this.allowCommands, dataConfiguration, this.lifecycle);
   }

   public LevelSettings copy() {
      return new LevelSettings(this.levelName, this.gameType, this.difficultySettings, this.allowCommands, this.dataConfiguration, this.lifecycle);
   }

   public LevelSettings withLifecycle(Lifecycle lifecycle) {
      return new LevelSettings(this.levelName, this.gameType, this.difficultySettings, this.allowCommands, this.dataConfiguration, lifecycle);
   }

   public record DifficultySettings(Difficulty difficulty, boolean hardcore, boolean locked) {
      public static final LevelSettings.DifficultySettings DEFAULT = new LevelSettings.DifficultySettings(Difficulty.NORMAL, false, false);
      public static final Codec<LevelSettings.DifficultySettings> CODEC = RecordCodecBuilder.create(
         i -> i.group(
               Difficulty.CODEC.fieldOf("difficulty").forGetter(LevelSettings.DifficultySettings::difficulty),
               Codec.BOOL.fieldOf("hardcore").forGetter(LevelSettings.DifficultySettings::hardcore),
               Codec.BOOL.fieldOf("locked").forGetter(LevelSettings.DifficultySettings::locked)
            )
            .apply(i, LevelSettings.DifficultySettings::new)
      );
   }
}
