import os
import json
import time
from typing import Dict, Tuple, Optional, List

import numpy as np

CONFIG_PATH = os.path.join("configs", "worldgen.json")


def load_config(path: str = CONFIG_PATH) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing config file at '{path}'. Create it at configs/worldgen.json."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _smoothstep(t: np.ndarray) -> np.ndarray:
    return t * t * (3.0 - 2.0 * t)


def value_noise_2d(w: int, h: int, grid: int, rng: np.random.Generator) -> np.ndarray:
    gx = max(2, (w // grid) + 2)
    gy = max(2, (h // grid) + 2)

    lattice = rng.random((gy, gx), dtype=np.float32)

    xs = np.linspace(0, gx - 2, w, dtype=np.float32)
    ys = np.linspace(0, gy - 2, h, dtype=np.float32)
    x0 = np.floor(xs).astype(np.int32)
    y0 = np.floor(ys).astype(np.int32)

    tx = _smoothstep(xs - x0)
    ty = _smoothstep(ys - y0)

    x0b = x0[None, :]
    y0b = y0[:, None]
    x1b = x0b + 1
    y1b = y0b + 1

    v00 = lattice[y0b, x0b]
    v10 = lattice[y0b, x1b]
    v01 = lattice[y1b, x0b]
    v11 = lattice[y1b, x1b]

    a = v00 * (1 - tx)[None, :] + v10 * tx[None, :]
    b = v01 * (1 - tx)[None, :] + v11 * tx[None, :]
    out = a * (1 - ty)[:, None] + b * ty[:, None]
    return out


def fbm_noise(
    w: int,
    h: int,
    base_grid: int,
    octaves: int,
    persistence: float,
    lacunarity: float,
    rng: np.random.Generator,
) -> np.ndarray:
    total = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    freq = 1.0
    amp_sum = 0.0

    for _ in range(octaves):
        grid = max(2, int(base_grid / freq))
        layer = value_noise_2d(w, h, grid, rng)
        total += layer * amp
        amp_sum += amp
        amp *= persistence
        freq *= lacunarity

    total /= max(1e-6, amp_sum)
    return total


def normalize01(a: np.ndarray) -> np.ndarray:
    mn = float(a.min())
    mx = float(a.max())
    if mx - mn < 1e-8:
        return np.zeros_like(a, dtype=np.float32)
    return ((a - mn) / (mx - mn)).astype(np.float32)


def biome_names() -> Dict[int, str]:
    return {
        0: "deep_water",
        1: "shallow_water",
        2: "beach",
        3: "grassland",
        4: "forest",
        5: "swamp",
        6: "savanna",
        7: "desert",
        8: "hill",
        9: "mountain",
        10: "snow",
    }


def biome_codes() -> Dict[str, int]:
    inv = {}
    for k, v in biome_names().items():
        inv[v] = k
    return inv


def island_mask(
    w: int,
    h: int,
    radius: float,
    edge_falloff: float,
    center_jitter: float,
    rng: np.random.Generator,
) -> np.ndarray:
    cx = 0.5
    cy = 0.5
    if center_jitter > 0.0:
        cx += (rng.random() * 2 - 1) * center_jitter
        cy += (rng.random() * 2 - 1) * center_jitter

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx / (w - 1)) - cx
    ny = (yy / (h - 1)) - cy

    d = np.sqrt(nx * nx + ny * ny)
    t = np.clip(1.0 - (d / max(1e-6, radius)), 0.0, 1.0)
    return np.power(t, edge_falloff).astype(np.float32)


def _range_mask(val: np.ndarray, r: Optional[List[float]]) -> np.ndarray:
    if r is None:
        return np.ones_like(val, dtype=bool)
    lo, hi = float(r[0]), float(r[1])
    return (val >= lo) & (val < hi)


def classify_biomes_from_rules(
    height: np.ndarray,
    moisture: np.ndarray,
    temp: np.ndarray,
    sea_level: float,
    rules: list,
) -> np.ndarray:
    h, w = height.shape
    codes = biome_codes()

    biome = np.full((h, w), codes["grassland"], dtype=np.uint8)

    water = height < float(sea_level)
    biome[water] = codes["deep_water"]

    land = ~water
    unassigned = land.copy()

    for rule in rules:
        name = rule.get("name", None)
        if not name or name not in codes:
            continue

        hm = _range_mask(height, rule.get("height"))
        mm = _range_mask(moisture, rule.get("moisture"))
        tm = _range_mask(temp, rule.get("temp"))

        match = unassigned & hm & mm & tm
        if np.any(match):
            biome[match] = codes[name]
            unassigned[match] = False

    return biome


def compute_shallow_ring(biome: np.ndarray, band_pixels: int) -> np.ndarray:
    deep = biome_codes()["deep_water"]
    water = (biome == deep)
    land = ~water

    h, w = biome.shape
    INF = 10**9
    dist = np.full((h, w), INF, dtype=np.int32)
    dist[land] = 0

    for y in range(h):
        row = dist[y]
        up = dist[y - 1] if y > 0 else None
        for x in range(w):
            best = row[x]
            if up is not None:
                best = min(best, up[x] + 1)
                if x > 0:
                    best = min(best, up[x - 1] + 2)
                if x + 1 < w:
                    best = min(best, up[x + 1] + 2)
            if x > 0:
                best = min(best, row[x - 1] + 1)
            row[x] = best

    for y in range(h - 1, -1, -1):
        row = dist[y]
        dn = dist[y + 1] if y + 1 < h else None
        for x in range(w - 1, -1, -1):
            best = row[x]
            if dn is not None:
                best = min(best, dn[x] + 1)
                if x > 0:
                    best = min(best, dn[x - 1] + 2)
                if x + 1 < w:
                    best = min(best, dn[x + 1] + 2)
            if x + 1 < w:
                best = min(best, row[x + 1] + 1)
            row[x] = best

    return water & (dist <= int(band_pixels))


def place_decorators(
    biome: np.ndarray,
    rng: np.random.Generator,
    densities: Dict[str, float],
    noise: np.ndarray,
) -> np.ndarray:
    h, w = biome.shape
    out = np.zeros((h, w), dtype=bool)
    names = biome_names()

    r = rng.random((h, w), dtype=np.float32)
    for code, bname in names.items():
        d = float(densities.get(bname, 0.0))
        if d <= 0:
            continue
        mask = (biome == code)
        if not np.any(mask):
            continue

        score = 0.55 * r + 0.45 * noise
        thresh = 1.0 - np.clip(d, 0.0, 0.95)
        out |= mask & (score >= thresh)

    return out


def place_ore_type(
    height: np.ndarray,
    biome: np.ndarray,
    rng: np.random.Generator,
    ore_cfg: dict,
    clump_noise: np.ndarray,
) -> np.ndarray:
    h, w = height.shape
    out = np.zeros((h, w), dtype=bool)

    min_h = float(ore_cfg.get("min_height", 0.0))
    max_h = float(ore_cfg.get("max_height", 1.01))
    dens_map = ore_cfg.get("per_biome_density", {})

    valid_height = (height >= min_h) & (height < max_h)

    names = biome_names()
    r = rng.random((h, w), dtype=np.float32)

    for code, bname in names.items():
        d = float(dens_map.get(bname, 0.0))
        if d <= 0:
            continue
        bm = (biome == code)
        if not np.any(bm):
            continue

        thresh = 1.0 - np.clip(d, 0.0, 0.25)
        score = 0.65 * clump_noise + 0.35 * r
        out |= bm & valid_height & (score >= thresh)

    return out


def generate_world_data(config_path: str = CONFIG_PATH) -> Tuple[list, list]:
    cfg = load_config(config_path)

    W = int(cfg["window"]["width"])
    H = int(cfg["window"]["height"])

    gen = cfg["generation"]
    seed = gen.get("seed", None)
    if seed is None:
        seed = int(time.time() * 1000) & 0xFFFFFFFF
    seed = int(seed)

    rng = np.random.default_rng(seed)

    octaves = int(gen["octaves"])
    persistence = float(gen["persistence"])
    lacunarity = float(gen["lacunarity"])

    island = gen["island"]
    radius = float(island["radius"])
    edge_falloff = float(island["edge_falloff"])
    center_jitter = float(island["center_jitter"])

    sea_level = float(gen["sea_level"])

    base_grid = max(24, min(W, H) // 6)

    height_noise = normalize01(fbm_noise(W, H, base_grid, octaves, persistence, lacunarity, rng))
    moisture = normalize01(fbm_noise(W, H, base_grid, max(3, octaves - 1), persistence, lacunarity, rng))
    temp = normalize01(fbm_noise(W, H, base_grid, max(3, octaves - 1), persistence, lacunarity, rng))

    mask = island_mask(W, H, radius, edge_falloff, center_jitter, rng)

    heightmap = normalize01(0.70 * height_noise + 0.30 * mask)
    heightmap = heightmap * (0.30 + 0.70 * mask)
    heightmap = normalize01(heightmap)

    rules = cfg["biomes"].get("rules", [])
    biome = classify_biomes_from_rules(heightmap, moisture, temp, sea_level, rules)

    shallow_cfg = gen.get("shallow_water", {})
    if shallow_cfg.get("enabled", True):
        band = int(shallow_cfg.get("band_pixels", 14))
        shallow = compute_shallow_ring(biome, band_pixels=band)
        biome[shallow] = biome_codes()["shallow_water"]

    rng_dec = np.random.default_rng((seed ^ (int(time.time() * 1000) & 0xFFFFFFFF)) & 0xFFFFFFFF)
    decorator_noise = normalize01(value_noise_2d(W, H, grid=max(12, min(W, H) // 10), rng=rng_dec))

    dec = cfg.get("decorators", {})
    trees_mask = np.zeros((H, W), dtype=bool)
    bushes_mask = np.zeros((H, W), dtype=bool)
    grass_mask = np.zeros((H, W), dtype=bool)

    if dec.get("trees", {}).get("enabled", True):
        tdens = dec["trees"].get("per_biome_density", {})
        trees_mask = place_decorators(biome, rng_dec, tdens, decorator_noise)

    if dec.get("bushes", {}).get("enabled", True):
        bdens = dec["bushes"].get("per_biome_density", {})
        bushes_mask = place_decorators(biome, rng_dec, bdens, decorator_noise)

    if dec.get("grass", {}).get("enabled", True):
        gdens = dec["grass"].get("per_biome_density", {})
        grass_mask = place_decorators(biome, rng_dec, gdens, decorator_noise)

    ores_cfg = cfg.get("ores", {})
    ore_masks: Dict[str, np.ndarray] = {}
    if ores_cfg.get("enabled", True):
        ng = int(ores_cfg.get("clumping", {}).get("noise_grid", 10))
        ore_noise = normalize01(value_noise_2d(W, H, grid=max(6, ng), rng=rng_dec))
        for ore in ores_cfg.get("types", []):
            ore_name = str(ore.get("name", "ore"))
            ore_masks[ore_name] = place_ore_type(heightmap, biome, rng_dec, ore, ore_noise)

    name_map = biome_names()

    world_tiles: List[List[dict]] = []
    object_tiles: List[List[dict]] = []

    obj_type = np.full((H, W), None, dtype=object)

    obj_type[grass_mask] = "grass"
    obj_type[bushes_mask] = "bush"
    obj_type[trees_mask] = "tree"
    for ore_name, m in ore_masks.items():
        obj_type[m] = ore_name

    for y in range(H):
        wrow = []
        orow = []
        for x in range(W):
            wrow.append({"pos": (x, y), "type": name_map[int(biome[y, x])]})
            t = obj_type[y, x]
            orow.append({"pos": (x, y), "type": None if t is None else str(t)})
        world_tiles.append(wrow)
        object_tiles.append(orow)

    deep = biome_codes()["deep_water"]
    non_sea = int(np.count_nonzero(biome != deep))
    print(f"[WORLD] seed={seed} size={W}x{H} non-sea-tiles={non_sea}")

    return world_tiles, object_tiles


if __name__ == "__main__":
    world_tiles, object_tiles = generate_world_data()
    print("[SAMPLE] world_tiles[0][0] =", world_tiles[0][0])
    print("[SAMPLE] object_tiles[0][0] =", object_tiles[0][0])