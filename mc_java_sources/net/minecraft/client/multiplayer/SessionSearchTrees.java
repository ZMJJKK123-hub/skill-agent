package net.minecraft.client.multiplayer;

import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Stream;
import net.minecraft.ChatFormatting;
import net.minecraft.client.ClientRecipeBook;
import net.minecraft.client.gui.screens.recipebook.RecipeCollection;
import net.minecraft.client.searchtree.FullTextSearchTree;
import net.minecraft.client.searchtree.IdSearchTree;
import net.minecraft.client.searchtree.SearchTree;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.util.Util;
import net.minecraft.util.context.ContextMap;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.crafting.display.SlotDisplayContext;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.CreativeModeTabSearchRegistry;

@OnlyIn(Dist.CLIENT)
public class SessionSearchTrees {
   private static final SessionSearchTrees.Key RECIPE_COLLECTIONS = new SessionSearchTrees.Key();
   public static final SessionSearchTrees.Key CREATIVE_NAMES = new SessionSearchTrees.Key();
   public static final SessionSearchTrees.Key CREATIVE_TAGS = new SessionSearchTrees.Key();
   private CompletableFuture<SearchTree<ItemStack>> EMPTY = CompletableFuture.completedFuture(SearchTree.empty());
   private Map<SessionSearchTrees.Key, CompletableFuture<SearchTree<ItemStack>>> creativeSearch = new IdentityHashMap<>();
   private CompletableFuture<SearchTree<RecipeCollection>> recipeSearch = CompletableFuture.completedFuture(SearchTree.empty());
   private final Map<SessionSearchTrees.Key, Runnable> reloaders = new IdentityHashMap<>();

   private void register(SessionSearchTrees.Key location, Runnable updater) {
      updater.run();
      this.reloaders.put(location, updater);
   }

   public void rebuildAfterLanguageChange() {
      for (Runnable value : this.reloaders.values()) {
         value.run();
      }
   }

   private static Stream<String> getTooltipLines(Stream<ItemStack> items, Item.TooltipContext context, TooltipFlag flag) {
      return items.<Component>flatMap(item -> item.getTooltipLines(context, null, flag).stream())
         .map(l -> ChatFormatting.stripFormatting(l.getString()).trim())
         .filter(s -> !s.isEmpty());
   }

   public void updateRecipes(ClientRecipeBook recipeBook, Level level) {
      this.register(
         RECIPE_COLLECTIONS,
         () -> {
            List<RecipeCollection> recipes = recipeBook.getCollections();
            RegistryAccess registryAccess = level.registryAccess();
            Registry<Item> itemRegistries = registryAccess.lookupOrThrow(Registries.ITEM);
            Item.TooltipContext tooltipContext = Item.TooltipContext.of(registryAccess);
            ContextMap recipeContext = SlotDisplayContext.fromLevel(level);
            TooltipFlag tooltipFlag = TooltipFlag.Default.NORMAL;
            CompletableFuture<?> previous = this.recipeSearch;
            this.recipeSearch = CompletableFuture.supplyAsync(
               () -> new FullTextSearchTree<>(
                  collection -> getTooltipLines(
                     collection.getRecipes().stream().flatMap(e -> e.resultItems(recipeContext).stream()), tooltipContext, tooltipFlag
                  ),
                  collection -> collection.getRecipes()
                     .stream()
                     .flatMap(e -> e.resultItems(recipeContext).stream())
                     .map(stack -> itemRegistries.getKey(stack.getItem())),
                  recipes
               ),
               Util.backgroundExecutor()
            );
            previous.cancel(true);
         }
      );
   }

   public SearchTree<RecipeCollection> recipes() {
      return this.recipeSearch.join();
   }

   public void updateCreativeTags(List<ItemStack> items) {
      for (Entry<CreativeModeTab, SessionSearchTrees.Key> entry : CreativeModeTabSearchRegistry.getTagSearchKeys().entrySet()) {
         this.register(
            entry.getValue(),
            () -> {
               List<ItemStack> tabItems = entry.getKey() == CreativeModeTabs.searchTab() ? items : List.copyOf(entry.getKey().getDisplayItems());
               CompletableFuture<?> previous = this.creativeSearch.getOrDefault(entry.getValue(), this.EMPTY);
               this.creativeSearch
                  .put(
                     entry.getValue(),
                     CompletableFuture.supplyAsync(
                        () -> new IdSearchTree<>(itemStack -> itemStack.tags().map(TagKey::location), tabItems), Util.backgroundExecutor()
                     )
                  );
               previous.cancel(true);
            }
         );
      }
   }

   public SearchTree<ItemStack> creativeTagSearch() {
      return this.getSearchTree(CREATIVE_TAGS);
   }

   public void updateCreativeTooltips(HolderLookup.Provider registries, List<ItemStack> itemStacks) {
      for (Entry<CreativeModeTab, SessionSearchTrees.Key> entry : CreativeModeTabSearchRegistry.getNameSearchKeys().entrySet()) {
         this.register(
            entry.getValue(),
            () -> {
               List<ItemStack> items = entry.getKey() == CreativeModeTabs.searchTab() ? itemStacks : List.copyOf(entry.getKey().getDisplayItems());
               Item.TooltipContext tooltipContext = Item.TooltipContext.of(registries);
               TooltipFlag tooltipFlag = TooltipFlag.Default.NORMAL.asCreative();
               CompletableFuture<?> previous = this.creativeSearch.getOrDefault(entry.getValue(), this.EMPTY);
               this.creativeSearch
                  .put(
                     entry.getValue(),
                     CompletableFuture.supplyAsync(
                        () -> new FullTextSearchTree<>(
                           itemStack -> getTooltipLines(Stream.of(itemStack), tooltipContext, tooltipFlag),
                           itemStack -> itemStack.typeHolder().unwrapKey().map(ResourceKey::identifier).stream(),
                           items
                        ),
                        Util.backgroundExecutor()
                     )
                  );
               previous.cancel(true);
            }
         );
      }
   }

   public SearchTree<ItemStack> creativeNameSearch() {
      return this.getSearchTree(CREATIVE_NAMES);
   }

   public SearchTree<ItemStack> getSearchTree(SessionSearchTrees.Key key) {
      return this.creativeSearch.getOrDefault(key, this.EMPTY).join();
   }

   @OnlyIn(Dist.CLIENT)
   public static class Key {
   }
}
