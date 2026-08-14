package net.minecraft.server.packs.resources;

import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;
import com.mojang.logging.LogUtils;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DynamicOps;
import com.mojang.serialization.JsonOps;
import java.io.IOException;
import java.io.Reader;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.Registry;
import net.minecraft.resources.FileToIdConverter;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.util.StrictJsonParser;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.common.crafting.conditions.ICondition;
import org.slf4j.Logger;

public abstract class SimpleJsonResourceReloadListener<T> extends SimplePreparableReloadListener<Map<Identifier, T>> {
   private static final Logger LOGGER = LogUtils.getLogger();
   private final DynamicOps<JsonElement> ops;
   private final Codec<T> codec;
   private final FileToIdConverter lister;

   protected SimpleJsonResourceReloadListener(HolderLookup.Provider registries, Codec<T> codec, ResourceKey<? extends Registry<T>> registryKey) {
      this(registries.createSerializationContext(JsonOps.INSTANCE), codec, FileToIdConverter.registry(registryKey));
   }

   protected SimpleJsonResourceReloadListener(
      HolderLookup.Provider registries, Codec<T> codec, ResourceKey<? extends Registry<T>> registryKey, ICondition.IContext context
   ) {
      this(context.wrap(registries.createSerializationContext(JsonOps.INSTANCE)), codec, FileToIdConverter.registry(registryKey));
   }

   protected SimpleJsonResourceReloadListener(Codec<T> codec, FileToIdConverter lister) {
      this(JsonOps.INSTANCE, codec, lister);
   }

   protected SimpleJsonResourceReloadListener(DynamicOps<JsonElement> ops, Codec<T> codec, FileToIdConverter lister) {
      this.ops = ops;
      this.codec = codec;
      this.lister = lister;
   }

   protected Map<Identifier, T> prepare(ResourceManager manager, ProfilerFiller profiler) {
      Map<Identifier, T> result = new HashMap<>();
      scanDirectory(manager, this.lister, this.ops, this.codec, result);
      return result;
   }

   public static <T> void scanDirectory(
      ResourceManager manager, ResourceKey<? extends Registry<T>> registryKey, DynamicOps<JsonElement> ops, Codec<T> codec, Map<Identifier, T> result
   ) {
      scanDirectory(manager, FileToIdConverter.registry(registryKey), ops, codec, result);
   }

   public static <T> void scanDirectory(
      ResourceManager manager, FileToIdConverter lister, DynamicOps<JsonElement> ops, Codec<T> codec, Map<Identifier, T> result
   ) {
      for (Entry<Identifier, Resource> entry : lister.listMatchingResources(manager).entrySet()) {
         Identifier location = entry.getKey();
         Identifier id = lister.fileToId(location);

         try (Reader reader = entry.getValue().openAsReader()) {
            JsonElement json = StrictJsonParser.parse(reader);
            json = ForgeHooks.readConditional(ops, json);
            if (json != null) {
               codec.parse(ops, json).ifSuccess(parsed -> {
                  parsed = ForgeHooks.onJsonDataParsed(codec, id, parsed);
                  if (parsed != null) {
                     if (result.putIfAbsent(id, (T)parsed) != null) {
                        throw new IllegalStateException("Duplicate data file ignored with ID " + id);
                     }
                  }
               }).ifError(error -> LOGGER.error("Couldn't parse data file '{}' from '{}': {}", new Object[]{id, location, error}));
            } else {
               LOGGER.debug("Skipping loading {} as its conditions were not met", location);
            }
         } catch (JsonParseException | IllegalArgumentException | IOException e) {
            LOGGER.error("Couldn't parse data file '{}' from '{}'", new Object[]{id, location, e});
         }
      }
   }
}
