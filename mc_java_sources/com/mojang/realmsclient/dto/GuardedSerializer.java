package com.mojang.realmsclient.dto;

import com.google.gson.ExclusionStrategy;
import com.google.gson.FieldAttributes;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public class GuardedSerializer {
   private static final ExclusionStrategy STRATEGY = new ExclusionStrategy() {
      public boolean shouldSkipClass(Class<?> clazz) {
         return false;
      }

      public boolean shouldSkipField(FieldAttributes field) {
         return field.getAnnotation(Exclude.class) != null;
      }
   };
   private final Gson gson = new GsonBuilder().addSerializationExclusionStrategy(STRATEGY).addDeserializationExclusionStrategy(STRATEGY).create();

   public String toJson(ReflectionBasedSerialization object) {
      return this.gson.toJson(object);
   }

   public String toJson(JsonElement jsonElement) {
      return this.gson.toJson(jsonElement);
   }

   public <T extends ReflectionBasedSerialization> @Nullable T fromJson(String contents, Class<T> cls) {
      return (T)this.gson.fromJson(contents, cls);
   }
}
