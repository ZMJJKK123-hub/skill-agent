// Starter: simple block + block item registration (copy into src/main/java).
// Rename the package and class, then call the helpers from your @Mod constructor.
package starter.block;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.function.Supplier;

public class BlockTemplate {

    public static <T extends Block> RegistryObject<T> register(
            DeferredRegister<Block> blocks,
            DeferredRegister<Item> items,
            String name,
            Supplier<T> block,
            String modid) {
        RegistryObject<T> obj = blocks.register(name, block);
        items.register(name, () -> new BlockItem(obj.get(),
                new Item.Properties().setId(items.key(name))));
        return obj;
    }

    // Example block: a simple full cube.
    public static BlockBehaviour.Properties simpleProperties(String name, DeferredRegister<Block> blocks) {
        return BlockBehaviour.Properties.of()
                .setId(blocks.key(name))
                .mapColor(MapColor.STONE)
                .strength(5.0F, 6.0F)
                .requiresCorrectToolForDrops()
                .sound(SoundType.STONE);
    }
}