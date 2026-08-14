package net.minecraft.world.item.crafting;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.List;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemStackTemplate;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.display.RecipeDisplay;
import net.minecraft.world.item.crafting.display.ShapelessCraftingRecipeDisplay;
import net.minecraft.world.item.crafting.display.SlotDisplay;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.util.RecipeMatcher;

public class ShapelessRecipe extends NormalCraftingRecipe {
   public static final MapCodec<ShapelessRecipe> MAP_CODEC = RecordCodecBuilder.mapCodec(
      i -> i.group(
            Recipe.CommonInfo.MAP_CODEC.forGetter(o -> o.commonInfo),
            CraftingRecipe.CraftingBookInfo.MAP_CODEC.forGetter(o -> o.bookInfo),
            ItemStackTemplate.CODEC.fieldOf("result").forGetter(o -> o.result),
            Ingredient.CODEC.listOf().fieldOf("ingredients").forGetter(o -> o.ingredients)
         )
         .apply(i, ShapelessRecipe::new)
   );
   public static final StreamCodec<RegistryFriendlyByteBuf, ShapelessRecipe> STREAM_CODEC = StreamCodec.composite(
      Recipe.CommonInfo.STREAM_CODEC,
      o -> o.commonInfo,
      CraftingRecipe.CraftingBookInfo.STREAM_CODEC,
      o -> o.bookInfo,
      ItemStackTemplate.STREAM_CODEC,
      o -> o.result,
      Ingredient.CONTENTS_STREAM_CODEC.apply(ByteBufCodecs.list()),
      o -> o.ingredients,
      ShapelessRecipe::new
   );
   public static final RecipeSerializer<ShapelessRecipe> SERIALIZER = new RecipeSerializer<>(MAP_CODEC, STREAM_CODEC);
   private final ItemStackTemplate result;
   private final List<Ingredient> ingredients;
   private final boolean isSimple;

   public ShapelessRecipe(Recipe.CommonInfo commonInfo, CraftingRecipe.CraftingBookInfo bookInfo, ItemStackTemplate result, List<Ingredient> ingredients) {
      super(commonInfo, bookInfo);
      this.result = result;
      this.ingredients = ingredients;
      this.isSimple = this.ingredients.stream().allMatch(Ingredient::isSimple);
   }

   @Override
   public RecipeSerializer<ShapelessRecipe> getSerializer() {
      return SERIALIZER;
   }

   @Override
   protected PlacementInfo createPlacementInfo() {
      return PlacementInfo.create(this.ingredients);
   }

   public boolean matches(CraftingInput input, Level level) {
      if (input.ingredientCount() != this.ingredients.size()) {
         return false;
      } else if (input.size() == 1 && this.ingredients.size() == 1) {
         return this.ingredients.getFirst().test(input.getItem(0));
      } else {
         return !this.isSimple ? RecipeMatcher.findMatches(input.items(), this.ingredients) != null : input.stackedContents().canCraft(this, null);
      }
   }

   public ItemStack assemble(CraftingInput input) {
      return this.result.create();
   }

   @Override
   public List<RecipeDisplay> display() {
      return List.of(
         new ShapelessCraftingRecipeDisplay(
            this.ingredients.stream().map(Ingredient::display).toList(),
            new SlotDisplay.ItemStackSlotDisplay(this.result),
            new SlotDisplay.ItemSlotDisplay(Items.CRAFTING_TABLE)
         )
      );
   }
}
