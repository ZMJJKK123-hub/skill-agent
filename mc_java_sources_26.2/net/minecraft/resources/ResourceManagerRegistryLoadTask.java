package net.minecraft.resources;

import com.google.gson.JsonElement;
import com.mojang.datafixers.util.Either;
import com.mojang.logging.LogUtils;
import com.mojang.serialization.Decoder;
import com.mojang.serialization.JsonOps;
import com.mojang.serialization.Lifecycle;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Map.Entry;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.function.Function;
import net.minecraft.core.Holder;
import net.minecraft.core.RegistrationInfo;
import net.minecraft.server.packs.repository.KnownPack;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.tags.TagKey;
import net.minecraft.tags.TagLoader;
import net.minecraft.util.Util;
import net.minecraft.util.thread.ParallelMapTransform;
import net.minecraftforge.common.crafting.conditions.ConditionCodec;
import org.slf4j.Logger;

public class ResourceManagerRegistryLoadTask<T> extends RegistryLoadTask<T> {
   private static final Logger LOGGER = LogUtils.getLogger();
   private static final Function<Optional<KnownPack>, RegistrationInfo> REGISTRATION_INFO_CACHE = Util.memoize(knownPack -> {
      Lifecycle lifecycle = knownPack.map(KnownPack::isVanilla).map(info -> Lifecycle.stable()).orElse(Lifecycle.experimental());
      return new RegistrationInfo(knownPack, lifecycle);
   });
   private final ResourceManager resourceManager;

   public ResourceManagerRegistryLoadTask(
      RegistryDataLoader.RegistryData<T> data, Lifecycle lifecycle, Map<ResourceKey<?>, Exception> loadingErrors, ResourceManager resourceManager
   ) {
      super(data, lifecycle, loadingErrors);
      this.resourceManager = resourceManager;
   }

   @Override
   public CompletableFuture<?> load(RegistryOps.RegistryInfoLookup context, Executor executor) {
      FileToIdConverter lister = FileToIdConverter.registry(this.registryKey());
      Decoder<Optional<T>> optionalCodec = ConditionCodec.wrap(this.data.elementCodec());
      return CompletableFuture.<Map<Identifier, Resource>>supplyAsync(() -> lister.listMatchingResources(this.resourceManager), executor)
         .thenCompose(registryResources -> {
            RegistryOps<JsonElement> ops = RegistryOps.create(JsonOps.INSTANCE, context);
            return ParallelMapTransform.schedule((Map<Identifier, Resource>)registryResources, (resourceId, thunk) -> {
               ResourceKey<T> elementKey = ResourceKey.create(this.registryKey(), lister.fileToId(resourceId));
               RegistrationInfo registrationInfo = REGISTRATION_INFO_CACHE.apply(thunk.knownPackInfo());
               Either<Optional<T>, Exception> result = RegistryLoadTask.PendingRegistration.loadFromResource(optionalCodec, ops, elementKey, thunk);
               if (!result.right().isPresent()) {
                  Optional<T> value = (Optional<T>)result.left().get();
                  if (value.isEmpty()) {
                     LOGGER.debug("Skipping {} conditions not met", elementKey);
                     return null;
                  }
               }

               return new RegistryLoadTask.PendingRegistration<>(elementKey, result.mapLeft(Optional::get), registrationInfo);
            }, executor);
         })
         .thenAcceptAsync(
            loadedEntries -> {
               this.registerElements(loadedEntries.entrySet().stream().sorted(Entry.comparingByKey()).map(Entry::getValue));
               TagLoader.ElementLookup<Holder<T>> tagElementLookup = TagLoader.ElementLookup.fromGetters(
                  this.registryKey(), this.concurrentRegistrationGetter, this.readOnlyRegistry()
               );
               Map<TagKey<T>, List<Holder<T>>> pendingTags = TagLoader.loadTagsForRegistry(this.resourceManager, this.registryKey(), tagElementLookup);
               this.registerTags(pendingTags);
            },
            executor
         );
   }
}
