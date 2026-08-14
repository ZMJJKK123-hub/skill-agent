package net.minecraft.world.entity;

import com.mojang.serialization.Codec;
import java.util.Arrays;
import java.util.Map;
import java.util.stream.Collectors;
import net.minecraft.util.StringRepresentable;
import net.minecraftforge.common.IExtensibleEnum;

public enum MobCategory implements StringRepresentable, IExtensibleEnum {
   MONSTER("monster", "MO", 70, false, false, 128),
   CREATURE("creature", "C", 10, true, true, 128),
   AMBIENT("ambient", "AM", 15, true, false, 128),
   AXOLOTLS("axolotls", "AX", 5, true, false, 128),
   UNDERGROUND_WATER_CREATURE("underground_water_creature", "UWC", 5, true, false, 128),
   WATER_CREATURE("water_creature", "WC", 5, true, false, 128),
   WATER_AMBIENT("water_ambient", "WA", 20, true, false, 64),
   MISC("misc", "MI", -1, true, true, 128);

   public static final Codec<MobCategory> CODEC = IExtensibleEnum.createCodecForExtensibleEnum(MobCategory::values, MobCategory::byName);
   private static final Map<String, MobCategory> BY_NAME = Arrays.stream(values())
      .collect(Collectors.toMap(MobCategory::getName, mobCategory -> (MobCategory)mobCategory));
   private final int max;
   private final boolean isFriendly;
   private final boolean isPersistent;
   private final String name;
   private final String debugAbbreviation;
   private final int noDespawnDistance = 32;
   private final int despawnDistance;

   MobCategory(
      final String name, final String debugAbbreviation, final int max, final boolean isFriendly, final boolean isPersistent, final int despawnDistance
   ) {
      this.name = name;
      this.debugAbbreviation = debugAbbreviation;
      this.max = max;
      this.isFriendly = isFriendly;
      this.isPersistent = isPersistent;
      this.despawnDistance = despawnDistance;
   }

   public String getName() {
      return this.name;
   }

   public String getDebugAbbreviation() {
      return this.debugAbbreviation;
   }

   @Override
   public String getSerializedName() {
      return this.name;
   }

   public int getMaxInstancesPerChunk() {
      return this.max;
   }

   public boolean isFriendly() {
      return this.isFriendly;
   }

   public boolean isPersistent() {
      return this.isPersistent;
   }

   public int getDespawnDistance() {
      return this.despawnDistance;
   }

   public int getNoDespawnDistance() {
      return 32;
   }

   public static MobCategory create(String name, String id, String debugAbbreviation, int max, boolean isFriendly, boolean isPersistent, int despawnDistance) {
      throw new IllegalStateException("Enum not extended");
   }

   @Deprecated
   @Override
   public void init() {
      BY_NAME.put(this.getName(), this);
   }

   public static MobCategory byName(String name) {
      return BY_NAME.get(name);
   }
}
