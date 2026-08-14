package net.minecraft.world.item.crafting;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Stream;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.HolderSetCodec;
import net.minecraft.util.ExtraCodecs;
import net.minecraft.world.entity.player.StackedContents;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.display.SlotDisplay;
import net.minecraft.world.level.ItemLike;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.common.crafting.ingredients.IIngredientSerializer;

public class Ingredient implements Predicate<ItemStack>, StackedContents.IngredientInfo<Holder<Item>> {
   private static final StreamCodec<RegistryFriendlyByteBuf, Ingredient> VANILLA_CONTENTS_STREAM_CODEC = ByteBufCodecs.holderSet(Registries.ITEM)
      .map(Ingredient::new, i -> i.values);
   public static final StreamCodec<RegistryFriendlyByteBuf, Ingredient> CONTENTS_STREAM_CODEC = ForgeHooks.ingredientStreamCodec();
   public static final StreamCodec<RegistryFriendlyByteBuf, Optional<Ingredient>> OPTIONAL_CONTENTS_STREAM_CODEC = CONTENTS_STREAM_CODEC.map(
      ingredient -> ingredient.items().count() == 0L ? Optional.empty() : Optional.of(ingredient), ingredient -> ingredient.orElseGet(() -> of())
   );
   public static final Codec<HolderSet<Item>> NON_AIR_HOLDER_SET_CODEC = HolderSetCodec.create(Registries.ITEM, Item.CODEC, false);
   private static final Codec<Ingredient> VANILLA_CODEC = ExtraCodecs.nonEmptyHolderSet(NON_AIR_HOLDER_SET_CODEC).xmap(Ingredient::new, i -> i.values);
   private static final MapCodec<Ingredient> VANILLA_MAP_CODEC = VANILLA_CODEC.fieldOf("value");
   public static final Codec<Ingredient> CODEC = ForgeHooks.ingredientBaseCodec(VANILLA_CODEC);
   protected final HolderSet<Item> values;
   private final boolean isVanilla = this.getClass() == Ingredient.class;
   public static final IIngredientSerializer<Ingredient> VANILLA_SERIALIZER = new IIngredientSerializer<Ingredient>() {
      @Override
      public MapCodec<? extends Ingredient> codec() {
         return Ingredient.VANILLA_MAP_CODEC;
      }

      @Override
      public void write(RegistryFriendlyByteBuf buffer, Ingredient value) {
         Ingredient.VANILLA_CONTENTS_STREAM_CODEC.encode(buffer, value);
      }

      @Override
      public Ingredient read(RegistryFriendlyByteBuf buffer) {
         return Ingredient.VANILLA_CONTENTS_STREAM_CODEC.decode(buffer);
      }
   };

   protected Ingredient(HolderSet<Item> values) {
      this(values, true);
   }

   protected Ingredient(HolderSet<Item> values, boolean validate) {
      if (validate) {
         values.unwrap().ifRight(directValues -> {
            if (directValues.isEmpty()) {
               throw new UnsupportedOperationException("Ingredients can't be empty");
            }

            if (directValues.contains(Items.AIR.builtInRegistryHolder())) {
               throw new UnsupportedOperationException("Ingredient can't contain air");
            }
         });
      }

      this.values = values;
   }

   public static boolean testOptionalIngredient(Optional<Ingredient> ingredient, ItemStack stack) {
      return ingredient.<Boolean>map(value -> value.test(stack)).orElseGet(stack::isEmpty);
   }

   @Deprecated
   public Stream<Holder<Item>> items() {
      return this.values.stream();
   }

   public boolean isEmpty() {
      return this.values.size() == 0;
   }

   public boolean test(ItemStack input) {
      return input.is(this.values);
   }

   public boolean acceptsItem(Holder<Item> item) {
      return this.values.contains(item);
   }

   @Override
   public boolean equals(Object o) {
      return o instanceof Ingredient other ? Objects.equals(this.values, other.values) : false;
   }

   @Override
   public int hashCode() {
      return Objects.hashCode(this.values);
   }

   public static Ingredient of(ItemLike itemLike) {
      return new Ingredient(HolderSet.direct(itemLike.asItem().builtInRegistryHolder()));
   }

   public static Ingredient of(ItemLike... items) {
      return of(Arrays.stream(items));
   }

   public static Ingredient of(Stream<? extends ItemLike> stream) {
      return new Ingredient(HolderSet.direct(stream.map(e -> e.asItem().builtInRegistryHolder()).toList()));
   }

   public static Ingredient of(HolderSet<Item> tag) {
      return new Ingredient(tag);
   }

   public SlotDisplay display() {
      return (SlotDisplay)this.values
         .unwrap()
         .map(SlotDisplay.TagSlotDisplay::new, l -> new SlotDisplay.Composite(l.stream().map(Ingredient::displayForSingleItem).toList()));
   }

   public static SlotDisplay optionalIngredientToDisplay(Optional<Ingredient> ingredient) {
      return ingredient.map(Ingredient::display).orElse(SlotDisplay.Empty.INSTANCE);
   }

   private static SlotDisplay displayForSingleItem(Holder<Item> item) {
      SlotDisplay inputDisplay = new SlotDisplay.ItemSlotDisplay(item);
      ItemStackTemplate remainderStack = item.value().getCraftingRemainder();
      if (remainderStack != null) {
         SlotDisplay remainderDisplay = new SlotDisplay.ItemStackSlotDisplay(remainderStack);
         return new SlotDisplay.WithRemainder(inputDisplay, remainderDisplay);
      } else {
         return inputDisplay;
      }
   }

   public boolean isSimple() {
      return true;
   }

   public final boolean isVanilla() {
      return this.isVanilla;
   }

   public IIngredientSerializer<? extends Ingredient> serializer() {
      if (!this.isVanilla()) {
         throw new IllegalStateException("Modders must implement Ingredient.codec in their custom Ingredients: " + this.getClass());
      } else {
         return VANILLA_SERIALIZER;
      }
   }

   @Override
   public String toString() {
      StringBuilder buf = new StringBuilder();
      buf.append("Ingredient[");

      for (int x = 0; x < this.values.size(); x++) {
         if (x != 0) {
            buf.append(", ");
         }

         buf.append(this.values.get(x));
      }

      buf.append(']');
      return buf.toString();
   }
}
