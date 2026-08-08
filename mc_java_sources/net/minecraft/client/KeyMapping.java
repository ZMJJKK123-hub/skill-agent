package net.minecraft.client;

import com.google.common.collect.Maps;
import com.mojang.blaze3d.platform.InputConstants;
import com.mojang.blaze3d.platform.Window;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Supplier;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.extensions.IForgeKeyMapping;
import net.minecraftforge.client.settings.IKeyConflictContext;
import net.minecraftforge.client.settings.KeyConflictContext;
import net.minecraftforge.client.settings.KeyMappingLookup;
import net.minecraftforge.client.settings.KeyModifier;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public class KeyMapping implements Comparable<KeyMapping>, IForgeKeyMapping {
   private static final Map<String, KeyMapping> ALL = Maps.newHashMap();
   private static final KeyMappingLookup MAP = new KeyMappingLookup();
   private final String name;
   private final InputConstants.Key defaultKey;
   private final KeyMapping.Category category;
   protected InputConstants.Key key;
   boolean isDown;
   private int clickCount;
   private final int order;
   private KeyModifier keyModifierDefault = KeyModifier.NONE;
   private KeyModifier keyModifier = KeyModifier.NONE;
   private IKeyConflictContext keyConflictContext = KeyConflictContext.UNIVERSAL;

   public static void click(InputConstants.Key key) {
      forAllKeyMappings(key, keyMapping -> keyMapping.clickCount++);
   }

   public static void set(InputConstants.Key key, boolean state) {
      forAllKeyMappings(key, keyMapping -> keyMapping.setDown(state));
   }

   private static void forAllKeyMappings(InputConstants.Key key, Consumer<KeyMapping> operation) {
      List<KeyMapping> keyMappings = MAP.getAll(key);
      if (keyMappings != null && !keyMappings.isEmpty()) {
         for (KeyMapping keyMapping : keyMappings) {
            operation.accept(keyMapping);
         }
      }
   }

   public static void setAll() {
      Window window = Minecraft.getInstance().getWindow();

      for (KeyMapping keyMapping : ALL.values()) {
         if (keyMapping.shouldSetOnIngameFocus()) {
            keyMapping.setDown(InputConstants.isKeyDown(window, keyMapping.key.getValue()));
         }
      }
   }

   public static void releaseAll() {
      for (KeyMapping keyMapping : ALL.values()) {
         keyMapping.release();
      }
   }

   public static void restoreToggleStatesOnScreenClosed() {
      for (KeyMapping keyMapping : ALL.values()) {
         if (keyMapping instanceof ToggleKeyMapping toggleKeyMapping && toggleKeyMapping.shouldRestoreStateOnScreenClosed()) {
            toggleKeyMapping.setDown(true);
         }
      }
   }

   public static void resetToggleKeys() {
      for (KeyMapping keyMapping : ALL.values()) {
         if (keyMapping instanceof ToggleKeyMapping toggleKeyMapping) {
            toggleKeyMapping.reset();
         }
      }
   }

   public static void resetMapping() {
      MAP.clear();

      for (KeyMapping keyMapping : ALL.values()) {
         keyMapping.registerMapping(keyMapping.key);
      }
   }

   public KeyMapping(String name, int keysym, KeyMapping.Category category) {
      this(name, InputConstants.Type.KEYSYM, keysym, category);
   }

   public KeyMapping(String name, InputConstants.Type type, int value, KeyMapping.Category category) {
      this(name, type, value, category, 0);
   }

   public KeyMapping(String name, InputConstants.Type type, int value, KeyMapping.Category category, int order) {
      this.name = name;
      this.key = type.getOrCreate(value);
      this.defaultKey = this.key;
      this.category = category;
      this.order = order;
      ALL.put(name, this);
      this.registerMapping(this.key);
   }

   public boolean isDown() {
      return this.isDown && this.isConflictContextAndModifierActive();
   }

   public KeyMapping.Category getCategory() {
      return this.category;
   }

   public boolean consumeClick() {
      if (this.clickCount == 0) {
         return false;
      }

      this.clickCount--;
      return true;
   }

   protected void release() {
      this.clickCount = 0;
      this.setDown(false);
   }

   protected boolean shouldSetOnIngameFocus() {
      return this.key.getType() == InputConstants.Type.KEYSYM && this.key.getValue() != InputConstants.UNKNOWN.getValue();
   }

   public String getName() {
      return this.name;
   }

   public InputConstants.Key getDefaultKey() {
      return this.defaultKey;
   }

   public void setKey(InputConstants.Key key) {
      this.key = key;
   }

   public int compareTo(KeyMapping o) {
      if (this.category == o.category) {
         return this.order == o.order ? I18n.get(this.name).compareTo(I18n.get(o.name)) : Integer.compare(this.order, o.order);
      } else {
         return compareSort(this.category, o.category);
      }
   }

   private static int compareSort(KeyMapping.Category c1, KeyMapping.Category c2) {
      int o1 = KeyMapping.Category.SORT_ORDER.indexOf(c1);
      int o2 = KeyMapping.Category.SORT_ORDER.indexOf(c2);
      if (o1 == -1 && o2 != -1) {
         return 1;
      } else if (o1 != -1 && o2 == -1) {
         return -1;
      } else {
         return o1 == -1 && o2 == -1 ? I18n.get(c1.id().toLanguageKey("key.category")).compareTo(I18n.get(c1.id().toLanguageKey("key.category"))) : o1 - o2;
      }
   }

   public static Supplier<Component> createNameSupplier(String key) {
      KeyMapping map = ALL.get(key);
      return map == null ? () -> Component.translatable(key) : map::getTranslatedKeyMessage;
   }

   public boolean same(KeyMapping that) {
      if (this.getKeyConflictContext().conflicts(that.getKeyConflictContext()) || that.getKeyConflictContext().conflicts(this.getKeyConflictContext())) {
         KeyModifier keyModifier = this.getKeyModifier();
         KeyModifier otherKeyModifier = that.getKeyModifier();
         if (keyModifier.matches(that.getKey()) || otherKeyModifier.matches(this.getKey())) {
            return true;
         }

         if (this.getKey().equals(that.getKey())) {
            return keyModifier == otherKeyModifier
               || this.getKeyConflictContext().conflicts(KeyConflictContext.IN_GAME)
                  && (keyModifier == KeyModifier.NONE || otherKeyModifier == KeyModifier.NONE);
         }
      }

      return this.key.equals(that.key);
   }

   public boolean isUnbound() {
      return this.key.equals(InputConstants.UNKNOWN);
   }

   public boolean matches(KeyEvent event) {
      return event.key() == InputConstants.UNKNOWN.getValue()
         ? this.key.getType() == InputConstants.Type.SCANCODE && this.key.getValue() == event.scancode()
         : this.key.getType() == InputConstants.Type.KEYSYM && this.key.getValue() == event.key();
   }

   public boolean matchesMouse(MouseButtonEvent event) {
      return this.key.getType() == InputConstants.Type.MOUSE && this.key.getValue() == event.button();
   }

   public boolean matches(InputConstants.Key key) {
      return this.key.equals(key);
   }

   public Component getTranslatedKeyMessage() {
      return this.getKeyModifier().getCombinedName(this.key, () -> this.key.getDisplayName());
   }

   public boolean isDefault() {
      return this.key.equals(this.defaultKey) && this.getKeyModifier() == this.getDefaultKeyModifier();
   }

   public String saveString() {
      return this.key.getName();
   }

   public void setDown(boolean down) {
      this.isDown = down;
   }

   private void registerMapping(InputConstants.Key key) {
      MAP.put(key, this);
   }

   public static @Nullable KeyMapping get(String name) {
      return ALL.get(name);
   }

   public KeyMapping(
      String description, IKeyConflictContext keyConflictContext, InputConstants.Type inputType, int keyCode, KeyMapping.Category category, int order
   ) {
      this(description, keyConflictContext, inputType.getOrCreate(keyCode), category, order);
   }

   public KeyMapping(String description, IKeyConflictContext keyConflictContext, InputConstants.Key keyCode, KeyMapping.Category category, int order) {
      this(description, keyConflictContext, KeyModifier.NONE, keyCode, category, order);
   }

   public KeyMapping(
      String description,
      IKeyConflictContext keyConflictContext,
      KeyModifier keyModifier,
      InputConstants.Type inputType,
      int keyCode,
      KeyMapping.Category category,
      int order
   ) {
      this(description, keyConflictContext, keyModifier, inputType.getOrCreate(keyCode), category, order);
   }

   public KeyMapping(
      String description, IKeyConflictContext keyConflictContext, KeyModifier keyModifier, InputConstants.Key keyCode, KeyMapping.Category category, int order
   ) {
      this.name = description;
      this.key = keyCode;
      this.defaultKey = keyCode;
      this.category = category;
      this.keyConflictContext = keyConflictContext;
      this.keyModifier = keyModifier;
      this.keyModifierDefault = keyModifier;
      this.order = order;
      if (this.keyModifier.matches(keyCode)) {
         this.keyModifier = KeyModifier.NONE;
      }

      ALL.put(description, this);
      MAP.put(keyCode, this);
   }

   @Override
   public InputConstants.Key getKey() {
      return this.key;
   }

   @Override
   public void setKeyConflictContext(IKeyConflictContext keyConflictContext) {
      this.keyConflictContext = keyConflictContext;
   }

   @Override
   public IKeyConflictContext getKeyConflictContext() {
      return this.keyConflictContext;
   }

   @Override
   public KeyModifier getDefaultKeyModifier() {
      return this.keyModifierDefault;
   }

   @Override
   public KeyModifier getKeyModifier() {
      return this.keyModifier;
   }

   @Override
   public void setKeyModifierAndCode(@org.jetbrains.annotations.Nullable KeyModifier keyModifier, InputConstants.Key keyCode) {
      MAP.remove(this);
      if (keyModifier == null) {
         keyModifier = KeyModifier.getModifier(this.key);
      }

      if (keyModifier == null || keyCode == InputConstants.UNKNOWN || KeyModifier.isKeyCodeModifier(keyCode)) {
         keyModifier = KeyModifier.NONE;
      }

      this.key = keyCode;
      this.keyModifier = keyModifier;
      MAP.put(keyCode, this);
   }

   @OnlyIn(Dist.CLIENT)
   public record Category(Identifier id) {
      private static final List<KeyMapping.Category> SORT_ORDER = new ArrayList<>();
      public static final KeyMapping.Category MOVEMENT = register("movement");
      public static final KeyMapping.Category MISC = register("misc");
      public static final KeyMapping.Category MULTIPLAYER = register("multiplayer");
      public static final KeyMapping.Category GAMEPLAY = register("gameplay");
      public static final KeyMapping.Category INVENTORY = register("inventory");
      public static final KeyMapping.Category CREATIVE = register("creative");
      public static final KeyMapping.Category SPECTATOR = register("spectator");
      public static final KeyMapping.Category DEBUG = register("debug");

      private static KeyMapping.Category register(String name) {
         return register(Identifier.withDefaultNamespace(name));
      }

      public static KeyMapping.Category register(Identifier id) {
         KeyMapping.Category category = new KeyMapping.Category(id);
         if (SORT_ORDER.contains(category)) {
            throw new IllegalArgumentException(String.format(Locale.ROOT, "Category '%s' is already registered.", id));
         }

         SORT_ORDER.add(category);
         return category;
      }

      public Component label() {
         return Component.translatable(this.id.toLanguageKey("key.category"));
      }
   }
}
