package net.minecraft.client.resources.model.cuboid;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import java.lang.reflect.Type;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public record ItemTransforms(
   ItemTransform thirdPersonLeftHand,
   ItemTransform thirdPersonRightHand,
   ItemTransform firstPersonLeftHand,
   ItemTransform firstPersonRightHand,
   ItemTransform head,
   ItemTransform gui,
   ItemTransform ground,
   ItemTransform fixed,
   ItemTransform fixedFromBottom,
   ImmutableMap<ItemDisplayContext, ItemTransform> moddedTransforms
) {
   public static final ItemTransforms NO_TRANSFORMS = new ItemTransforms(
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM,
      ItemTransform.NO_TRANSFORM
   );

   @Deprecated
   public ItemTransforms(
      ItemTransform thirdPersonLeftHand,
      ItemTransform thirdPersonRightHand,
      ItemTransform firstPersonLeftHand,
      ItemTransform firstPersonRightHand,
      ItemTransform head,
      ItemTransform gui,
      ItemTransform ground,
      ItemTransform fixed,
      ItemTransform fixedFromBottom
   ) {
      this(thirdPersonLeftHand, thirdPersonRightHand, firstPersonLeftHand, firstPersonRightHand, head, gui, ground, fixed, fixedFromBottom, ImmutableMap.of());
   }

   public ItemTransform getTransform(ItemDisplayContext type) {
      return switch (type) {
         case THIRD_PERSON_LEFT_HAND -> this.thirdPersonLeftHand;
         case THIRD_PERSON_RIGHT_HAND -> this.thirdPersonRightHand;
         case FIRST_PERSON_LEFT_HAND -> this.firstPersonLeftHand;
         case FIRST_PERSON_RIGHT_HAND -> this.firstPersonRightHand;
         case HEAD -> this.head;
         case GUI -> this.gui;
         case GROUND -> this.ground;
         case FIXED -> this.fixed;
         case ON_SHELF -> this.fixedFromBottom;
         default -> (ItemTransform)this.moddedTransforms.getOrDefault(type, ItemTransform.NO_TRANSFORM);
      };
   }

   @OnlyIn(Dist.CLIENT)
   protected static class Deserializer implements JsonDeserializer<ItemTransforms> {
      public ItemTransforms deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context) throws JsonParseException {
         JsonObject object = json.getAsJsonObject();
         ItemTransform thirdPersonRightHand = this.getTransform(context, object, ItemDisplayContext.THIRD_PERSON_RIGHT_HAND);
         ItemTransform thirdPersonLeftHand = this.getTransform(context, object, ItemDisplayContext.THIRD_PERSON_LEFT_HAND);
         if (thirdPersonLeftHand == ItemTransform.NO_TRANSFORM) {
            thirdPersonLeftHand = thirdPersonRightHand;
         }

         ItemTransform firstPersonRightHand = this.getTransform(context, object, ItemDisplayContext.FIRST_PERSON_RIGHT_HAND);
         ItemTransform firstPersonLeftHand = this.getTransform(context, object, ItemDisplayContext.FIRST_PERSON_LEFT_HAND);
         if (firstPersonLeftHand == ItemTransform.NO_TRANSFORM) {
            firstPersonLeftHand = firstPersonRightHand;
         }

         ItemTransform head = this.getTransform(context, object, ItemDisplayContext.HEAD);
         ItemTransform gui = this.getTransform(context, object, ItemDisplayContext.GUI);
         ItemTransform ground = this.getTransform(context, object, ItemDisplayContext.GROUND);
         ItemTransform fixed = this.getTransform(context, object, ItemDisplayContext.FIXED);
         ItemTransform fixedFromBottom = this.getTransform(context, object, ItemDisplayContext.ON_SHELF);
         Builder<ItemDisplayContext, ItemTransform> builder = ImmutableMap.builder();

         for (ItemDisplayContext type : ItemDisplayContext.values()) {
            if (type.isModded()) {
               ItemTransform transform = this.getTransform(context, object, type);

               for (ItemDisplayContext fallbackType = type;
                  transform == ItemTransform.NO_TRANSFORM && fallbackType.fallback() != null;
                  transform = this.getTransform(context, object, fallbackType)
               ) {
                  fallbackType = fallbackType.fallback();
               }

               if (transform != ItemTransform.NO_TRANSFORM) {
                  builder.put(type, transform);
               }
            }
         }

         return new ItemTransforms(
            thirdPersonLeftHand, thirdPersonRightHand, firstPersonLeftHand, firstPersonRightHand, head, gui, ground, fixed, fixedFromBottom
         );
      }

      private ItemTransform getTransform(JsonDeserializationContext context, JsonObject object, ItemDisplayContext transform) {
         String name = transform.getSerializedName();
         return object.has(name) ? (ItemTransform)context.deserialize(object.get(name), ItemTransform.class) : ItemTransform.NO_TRANSFORM;
      }
   }
}
