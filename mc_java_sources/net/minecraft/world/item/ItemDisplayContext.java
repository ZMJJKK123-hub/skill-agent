package net.minecraft.world.item;

import com.mojang.serialization.Codec;
import java.util.Objects;
import java.util.function.IntFunction;
import javax.annotation.Nullable;
import net.minecraft.resources.Identifier;
import net.minecraft.util.StringRepresentable;
import net.minecraftforge.common.IExtensibleEnum;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.IForgeRegistry;
import net.minecraftforge.registries.IForgeRegistryInternal;

public enum ItemDisplayContext implements StringRepresentable, IExtensibleEnum {
   NONE(0, "none"),
   THIRD_PERSON_LEFT_HAND(1, "thirdperson_lefthand"),
   THIRD_PERSON_RIGHT_HAND(2, "thirdperson_righthand"),
   FIRST_PERSON_LEFT_HAND(3, "firstperson_lefthand"),
   FIRST_PERSON_RIGHT_HAND(4, "firstperson_righthand"),
   HEAD(5, "head"),
   GUI(6, "gui"),
   GROUND(7, "ground"),
   FIXED(8, "fixed"),
   ON_SHELF(9, "on_shelf");

   public static final Codec<ItemDisplayContext> CODEC = Codec.lazyInitialized(() -> StringRepresentable.fromEnum(ItemDisplayContext::values));
   public static final IntFunction<ItemDisplayContext> BY_ID = id -> Objects.requireNonNullElse(
      ((IForgeRegistryInternal)ForgeRegistries.DISPLAY_CONTEXTS.get()).getValue(id < 0 ? 127 + -id : id), NONE
   );
   private byte id;
   private final String name;
   private final boolean isModded;
   @Nullable
   private final ItemDisplayContext fallback;
   public static final IForgeRegistry.AddCallback<ItemDisplayContext> ADD_CALLBACK = (owner, stage, id, key, obj, oldObj) -> obj.id = id > 127
      ? (byte)(-(id - 127))
      : (byte)id;

   ItemDisplayContext(final int id, final String name) {
      this.name = name;
      this.id = (byte)id;
      this.isModded = false;
      this.fallback = null;
   }

   @Override
   public String getSerializedName() {
      return this.name;
   }

   public byte getId() {
      return this.id;
   }

   public boolean firstPerson() {
      return this == FIRST_PERSON_LEFT_HAND || this == FIRST_PERSON_RIGHT_HAND;
   }

   public boolean leftHand() {
      return this == FIRST_PERSON_LEFT_HAND || this == THIRD_PERSON_LEFT_HAND;
   }

   ItemDisplayContext(Identifier serializeName, ItemDisplayContext fallback) {
      this.id = 0;
      this.name = Objects.requireNonNull(serializeName, "Modded ItemDisplayContexts must have a non-null serializeName").toString();
      this.isModded = true;
      this.fallback = fallback;
   }

   public boolean isModded() {
      return this.isModded;
   }

   @Nullable
   public ItemDisplayContext fallback() {
      return this.fallback;
   }

   public static ItemDisplayContext create(String keyName, Identifier serializedName, @Nullable ItemDisplayContext fallback) {
      throw new IllegalStateException("Enum not extended!");
   }
}
