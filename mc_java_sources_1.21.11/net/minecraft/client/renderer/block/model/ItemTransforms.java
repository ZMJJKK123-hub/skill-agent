package net.minecraft.client.renderer.block.model;

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
    com.google.common.collect.ImmutableMap<ItemDisplayContext, ItemTransform> moddedTransforms
) {

    @Deprecated
    public ItemTransforms(ItemTransform thirdPersonLeftHand, ItemTransform thirdPersonRightHand, ItemTransform firstPersonLeftHand, ItemTransform firstPersonRightHand, ItemTransform head, ItemTransform gui, ItemTransform ground, ItemTransform fixed, ItemTransform fixedFromBottom) {
        this(thirdPersonLeftHand, thirdPersonRightHand, firstPersonLeftHand, firstPersonRightHand, head, gui, ground, fixed, fixedFromBottom, com.google.common.collect.ImmutableMap.of());
    }

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

    public ItemTransform getTransform(ItemDisplayContext p_270619_) {
        return switch (p_270619_) {
            case THIRD_PERSON_LEFT_HAND -> this.thirdPersonLeftHand;
            case THIRD_PERSON_RIGHT_HAND -> this.thirdPersonRightHand;
            case FIRST_PERSON_LEFT_HAND -> this.firstPersonLeftHand;
            case FIRST_PERSON_RIGHT_HAND -> this.firstPersonRightHand;
            case HEAD -> this.head;
            case GUI -> this.gui;
            case GROUND -> this.ground;
            case FIXED -> this.fixed;
            case ON_SHELF -> this.fixedFromBottom;
            default -> moddedTransforms.getOrDefault(p_270619_, ItemTransform.NO_TRANSFORM);
        };
    }

    @OnlyIn(Dist.CLIENT)
    public static class Deserializer implements JsonDeserializer<ItemTransforms> {
        public ItemTransforms deserialize(JsonElement p_111820_, Type p_111821_, JsonDeserializationContext p_111822_) throws JsonParseException {
            JsonObject jsonobject = p_111820_.getAsJsonObject();
            ItemTransform itemtransform = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.THIRD_PERSON_RIGHT_HAND);
            ItemTransform itemtransform1 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.THIRD_PERSON_LEFT_HAND);
            if (itemtransform1 == ItemTransform.NO_TRANSFORM) {
                itemtransform1 = itemtransform;
            }

            ItemTransform itemtransform2 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.FIRST_PERSON_RIGHT_HAND);
            ItemTransform itemtransform3 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.FIRST_PERSON_LEFT_HAND);
            if (itemtransform3 == ItemTransform.NO_TRANSFORM) {
                itemtransform3 = itemtransform2;
            }

            ItemTransform itemtransform4 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.HEAD);
            ItemTransform itemtransform5 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.GUI);
            ItemTransform itemtransform6 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.GROUND);
            ItemTransform itemtransform7 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.FIXED);
            ItemTransform itemtransform8 = this.getTransform(p_111822_, jsonobject, ItemDisplayContext.ON_SHELF);
            var builder = com.google.common.collect.ImmutableMap.<ItemDisplayContext, ItemTransform>builder();
            for (ItemDisplayContext type : ItemDisplayContext.values()) {
               if (type.isModded()) {
                  var transform = this.getTransform(p_111822_, jsonobject, type);
                  var fallbackType = type;
                  while (transform == ItemTransform.NO_TRANSFORM && fallbackType.fallback() != null) {
                     fallbackType = fallbackType.fallback();
                     transform = this.getTransform(p_111822_, jsonobject, fallbackType);
                  }
                  if (transform != ItemTransform.NO_TRANSFORM)
                     builder.put(type, transform);
               }
            }

            return new ItemTransforms(
                itemtransform1, itemtransform, itemtransform3, itemtransform2, itemtransform4, itemtransform5, itemtransform6, itemtransform7, itemtransform8, builder.build()
            );
        }

        private ItemTransform getTransform(JsonDeserializationContext p_270385_, JsonObject p_270436_, ItemDisplayContext p_270100_) {
            String s = p_270100_.getSerializedName();
            return p_270436_.has(s) ? p_270385_.deserialize(p_270436_.get(s), ItemTransform.class) : ItemTransform.NO_TRANSFORM;
        }
    }
}
