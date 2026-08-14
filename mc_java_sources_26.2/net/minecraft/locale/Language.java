package net.minecraft.locale;

import com.google.common.collect.ImmutableList;
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import com.mojang.logging.LogUtils;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Map.Entry;
import java.util.function.BiConsumer;
import java.util.regex.Pattern;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.network.chat.Style;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.GsonHelper;
import net.minecraft.util.StringDecomposer;
import net.minecraftforge.common.ForgeI18n;
import net.minecraftforge.server.LanguageHook;
import org.slf4j.Logger;

public abstract class Language {
   private static final Logger LOGGER = LogUtils.getLogger();
   private static final Gson GSON = new Gson();
   private static final Pattern UNSUPPORTED_FORMAT_PATTERN = Pattern.compile("%(\\d+\\$)?[\\d.]*[df]");
   public static final String DEFAULT = "en_us";
   public static final Language DEFAULT_INSTANCE = loadDefault();
   private static volatile Language instance = DEFAULT_INSTANCE;

   private static Language loadDefault() {
      DeprecatedTranslationsInfo deprecatedInfo = DeprecatedTranslationsInfo.loadFromDefaultResource();
      final Map<String, String> loadedData = new HashMap<>();
      BiConsumer<String, String> output = loadedData::put;
      parseTranslations(output, "/assets/minecraft/lang/en_us.json");
      deprecatedInfo.applyToMap(loadedData);
      LanguageHook.captureLanguageMap(loadedData);
      final Map<String, String> storage = loadedData;
      return new Language() {
         @Override
         public String getOrDefault(String elementId, String defaultValue) {
            return storage.getOrDefault(elementId, defaultValue);
         }

         @Override
         public boolean has(String elementId) {
            return storage.containsKey(elementId);
         }

         @Override
         public boolean isDefaultRightToLeft() {
            return false;
         }

         @Override
         public FormattedCharSequence getVisualOrder(FormattedText logicalOrderText) {
            return outputx -> logicalOrderText.visit(
                  (style, contents) -> StringDecomposer.iterateFormatted(contents, style, output) ? Optional.empty() : FormattedText.STOP_ITERATION,
                  Style.EMPTY
               )
               .isPresent();
         }

         @Override
         public Map<String, String> getLanguageData() {
            return loadedData;
         }
      };
   }

   private static void parseTranslations(BiConsumer<String, String> output, String path) {
      try (InputStream stream = Language.class.getResourceAsStream(path)) {
         loadFromJson(stream, output);
      } catch (IOException | JsonParseException e) {
         LOGGER.error("Couldn't read strings from {}", path, e);
      }
   }

   public static void loadFromJson(InputStream stream, BiConsumer<String, String> output) {
      JsonObject entries = (JsonObject)GSON.fromJson(new InputStreamReader(stream, StandardCharsets.UTF_8), JsonObject.class);

      for (Entry<String, JsonElement> entry : entries.entrySet()) {
         String text = UNSUPPORTED_FORMAT_PATTERN.matcher(GsonHelper.convertToString(entry.getValue(), entry.getKey())).replaceAll("%$1s");
         output.accept(entry.getKey(), text);
      }
   }

   public static Language getInstance() {
      return instance;
   }

   public static void inject(Language language) {
      instance = language;
      ForgeI18n.loadLanguageData(language.getLanguageData());
   }

   public Map<String, String> getLanguageData() {
      return Map.of();
   }

   public String getOrDefault(String elementId) {
      return this.getOrDefault(elementId, elementId);
   }

   public abstract String getOrDefault(String var1, String var2);

   public abstract boolean has(String var1);

   public abstract boolean isDefaultRightToLeft();

   public abstract FormattedCharSequence getVisualOrder(FormattedText var1);

   public List<FormattedCharSequence> getVisualOrder(List<FormattedText> lines) {
      return lines.stream().map(this::getVisualOrder).collect(ImmutableList.toImmutableList());
   }
}
