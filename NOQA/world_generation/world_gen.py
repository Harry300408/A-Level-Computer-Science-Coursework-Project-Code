import os  # Standard library: filesystem checks (e.g., does a config file exist?)
import json  # Standard library: parse JSON config files
import time  # Standard library: used for time-based seeding when no seed is provided
from typing import Dict, Tuple, Optional, List  # Type hints for readability and tooling

import numpy as np  # NumPy: fast array math for noise fields and masks

CONFIG_PATH = "NOQA/world_generation/configs/world_gen_configs.json"  # Default path to config


def load_config(path: str = CONFIG_PATH) -> dict:  # Load the world generation config from JSON
    if not os.path.exists(path):  # Verify the file exists before trying to read it
        raise FileNotFoundError(  # Fail early with a helpful error message
            f"Missing config file at '{path}'. Create it at configs/world_gen_configs.json."  # Tell user where to create it
        )  # End raise
    with open(path, "r", encoding="utf-8") as f:  # Open JSON file safely with UTF-8
        return json.load(f)  # Parse JSON into Python dict and return it


def _smoothstep(t: np.ndarray) -> np.ndarray:  # Smooth interpolation curve for value noise blending
    # smoothstep makes interpolation less “blocky” than linear; it eases in/out at cell boundaries
    # Formula: 3t^2 - 2t^3 (implemented as t*t*(3-2t)), mapping [0,1] -> [0,1]
    return t * t * (3.0 - 2.0 * t)  # Apply cubic smoothing elementwise on array


def value_noise_2d(w: int, h: int, grid: int, rng: np.random.Generator) -> np.ndarray:
    # Generate 2D “value noise”:
    # - Make a coarse grid of random values (“lattice”)
    # - For each output pixel, find the surrounding lattice cell corners
    # - Interpolate between corner values (bilinear) using smoothstep to avoid harsh transitions

    gx = max(2, (w // grid) + 2)  # Lattice points in X: enough to cover width plus a border
    gy = max(2, (h // grid) + 2)  # Lattice points in Y: enough to cover height plus a border

    lattice = rng.random((gy, gx), dtype=np.float32)  # Random lattice values in [0,1), float32 for speed/memory

    xs = np.linspace(0, gx - 2, w, dtype=np.float32)  # Map pixel x positions into lattice-cell x coordinates
    ys = np.linspace(0, gy - 2, h, dtype=np.float32)  # Map pixel y positions into lattice-cell y coordinates
    x0 = np.floor(xs).astype(np.int32)  # Integer “left” lattice index for each output x
    y0 = np.floor(ys).astype(np.int32)  # Integer “top” lattice index for each output y

    tx = _smoothstep(xs - x0)  # Fraction across the cell in x (0..1) smoothed for nicer blending
    ty = _smoothstep(ys - y0)  # Fraction across the cell in y (0..1) smoothed for nicer blending

    x0b = x0[None, :]  # Broadcast x indices into 2D shape (1,w) for vectorized lattice sampling
    y0b = y0[:, None]  # Broadcast y indices into 2D shape (h,1) for vectorized lattice sampling
    x1b = x0b + 1  # “Right” lattice index = left + 1
    y1b = y0b + 1  # “Bottom” lattice index = top + 1

    v00 = lattice[y0b, x0b]  # Top-left corner value for every output pixel’s cell
    v10 = lattice[y0b, x1b]  # Top-right corner value
    v01 = lattice[y1b, x0b]  # Bottom-left corner value
    v11 = lattice[y1b, x1b]  # Bottom-right corner value

    a = v00 * (1 - tx)[None, :] + v10 * tx[None, :]  # Interpolate along x on the top edge
    b = v01 * (1 - tx)[None, :] + v11 * tx[None, :]  # Interpolate along x on the bottom edge
    out = a * (1 - ty)[:, None] + b * ty[:, None]  # Interpolate along y between top and bottom edges
    return out  # Return noise field (h,w) in ~[0,1]


def fbm_noise(
    w: int,  # output width
    h: int,  # output height
    base_grid: int,  # base cell size used to set frequency/detail level
    octaves: int,  # number of layers of noise to sum
    persistence: float,  # amplitude multiplier per octave (how fast contributions decay)
    lacunarity: float,  # frequency multiplier per octave (how fast detail increases)
    rng: np.random.Generator,  # random generator (deterministic if seed fixed)
) -> np.ndarray:
    # fBm (fractal Brownian motion) = sum of multiple noise octaves:
    # - Each octave: higher frequency (smaller features), lower amplitude (less influence)
    # - Produces natural-looking multi-scale variation (mountains/continents patterns)

    total = np.zeros((h, w), dtype=np.float32)  # Accumulator for combined noise layers
    amp = 1.0  # Starting amplitude for octave 0
    freq = 1.0  # Starting frequency factor for octave 0
    amp_sum = 0.0  # Track sum of amplitudes so we can normalize at the end

    for _ in range(octaves):  # Repeat for each octave
        grid = max(2, int(base_grid / freq))  # Convert frequency into a grid cell size (smaller grid => higher freq)
        layer = value_noise_2d(w, h, grid, rng)  # Generate one octave of value noise
        total += layer * amp  # Add this octave’s contribution to the total
        amp_sum += amp  # Accumulate amplitude for later normalization
        amp *= persistence  # Reduce amplitude for next octave (less influence)
        freq *= lacunarity  # Increase frequency for next octave (more detail)

    total /= max(1e-6, amp_sum)  # Normalize so result stays consistent even if octaves change
    return total  # Return fBm field (h,w)


def normalize01(a: np.ndarray) -> np.ndarray:
    # Normalize any array into [0,1] range using min-max scaling.
    mn = float(a.min())  # Minimum value in the array
    mx = float(a.max())  # Maximum value in the array
    if mx - mn < 1e-8:  # Guard: if array is constant or nearly constant
        return np.zeros_like(a, dtype=np.float32)  # Avoid divide-by-zero; return all zeros
    return ((a - mn) / (mx - mn)).astype(np.float32)  # Scale to [0,1] and ensure float32


def biome_names() -> Dict[int, str]:
    # Canonical mapping of numeric biome codes (compact for storage) to string names (human-readable)
    return {
        0: "deep_water",  # Ocean / deep water
        1: "shallow_water",  # Coastal shallow water band
        2: "beach",  # Sand near coast
        3: "grassland",  # Default land biome
        4: "forest",  # Forested biome
        5: "swamp",  # Wetland biome
        6: "savanna",  # Warm grassland
        7: "desert",  # Dry biome
        8: "hill",  # Elevated terrain
        9: "mountain",  # High elevation
        10: "snow",  # Cold/high biome
    }  # End mapping


def biome_codes() -> Dict[str, int]:
    # Invert biome_names() so you can look up numeric codes by name quickly
    inv = {}  # Start empty dict
    for k, v in biome_names().items():  # Iterate code->name pairs
        inv[v] = k  # Store name->code
    return inv  # Return inverted dict


def island_mask(
    w: int,  # map width
    h: int,  # map height
    radius: float,  # island radius in normalized coordinate space (roughly)
    edge_falloff: float,  # how sharply the island fades at edges (power exponent)
    center_jitter: float,  # random offset applied to center for variation
    rng: np.random.Generator,  # RNG for deterministic jitter
) -> np.ndarray:
    # Create an “island-shaped” radial mask:
    # - Values highest near center (~1)
    # - Decrease toward edges (~0)
    # - Applied to heightmap to encourage land in middle and water around edges

    cx = 0.5  # Base center x (normalized)
    cy = 0.5  # Base center y (normalized)
    if center_jitter > 0.0:  # If jitter enabled
        cx += (rng.random() * 2 - 1) * center_jitter  # Randomly move center x in [-jitter, +jitter]
        cy += (rng.random() * 2 - 1) * center_jitter  # Randomly move center y in [-jitter, +jitter]

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)  # Build coordinate grids of shape (h,w)
    nx = (xx / (w - 1)) - cx  # Normalize x to [0,1], then shift so center is at 0
    ny = (yy / (h - 1)) - cy  # Normalize y to [0,1], then shift so center is at 0

    d = np.sqrt(nx * nx + ny * ny)  # Euclidean distance from center for each pixel
    t = np.clip(1.0 - (d / max(1e-6, radius)), 0.0, 1.0)  # Convert distance into 1-at-center, 0-outside-radius
    return np.power(t, edge_falloff).astype(np.float32)  # Apply falloff exponent to shape shoreline steepness


def _range_mask(val: np.ndarray, r: Optional[List[float]]) -> np.ndarray:
    # Helper: build a boolean mask for values in a range [lo, hi).
    # If r is None, return all True (meaning “no constraint” for that dimension).
    if r is None:  # No range constraint given
        return np.ones_like(val, dtype=bool)  # Everything matches
    lo, hi = float(r[0]), float(r[1])  # Extract and cast endpoints
    return (val >= lo) & (val < hi)  # Half-open interval: includes lo, excludes hi


def classify_biomes_from_rules(
    height: np.ndarray,  # normalized height field (0..1)
    moisture: np.ndarray,  # normalized moisture field (0..1)
    temp: np.ndarray,  # normalized temperature field (0..1)
    sea_level: float,  # height threshold below which tiles are water
    rules: list,  # ordered list of biome classification rules from config
) -> np.ndarray:
    # Biome classification algorithm:
    # 1) Start with default land biome (grassland)
    # 2) Mark anything below sea_level as deep_water
    # 3) For remaining land tiles, apply rules in order:
    #    - each rule can specify ranges for height/moisture/temp
    #    - first rule that matches an unassigned land tile assigns its biome

    h, w = height.shape  # Extract dimensions (note: h rows, w columns)
    codes = biome_codes()  # Build name->code mapping for quick use

    biome = np.full((h, w), codes["grassland"], dtype=np.uint8)  # Initialize to grassland everywhere

    water = height < float(sea_level)  # Water where height is below sea level
    biome[water] = codes["deep_water"]  # Set water tiles to deep_water code

    land = ~water  # Land tiles are everything else
    unassigned = land.copy()  # Track land tiles not yet assigned by any rule

    for rule in rules:  # Apply each rule in order (priority order)
        name = rule.get("name", None)  # Biome name to assign for this rule
        if not name or name not in codes:  # Skip invalid rule entries
            continue  # Move to next rule

        hm = _range_mask(height, rule.get("height"))  # Height constraint mask (or all True)
        mm = _range_mask(moisture, rule.get("moisture"))  # Moisture constraint mask (or all True)
        tm = _range_mask(temp, rule.get("temp"))  # Temperature constraint mask (or all True)

        match = unassigned & hm & mm & tm  # Tiles that match rule AND are still unassigned land
        if np.any(match):  # Only do assignment work if there is at least one match
            biome[match] = codes[name]  # Assign the biome code for this rule
            unassigned[match] = False  # Mark these tiles as assigned so later rules don’t overwrite

    return biome  # Return biome code map


def compute_shallow_ring(biome: np.ndarray, band_pixels: int) -> np.ndarray:
    # Compute shallow-water ring:
    # - Start with deep water classification
    # - Compute distance from land into water via a 2-pass distance transform approximation
    # - Mark water tiles within band_pixels of land as “shallow” candidates

    deep = biome_codes()["deep_water"]  # Code for deep water
    water = (biome == deep)  # True for deep water tiles
    land = ~water  # Everything else treated as land for distance purposes

    h, w = biome.shape  # Dimensions
    INF = 10**9  # Large number representing “infinite” distance
    dist = np.full((h, w), INF, dtype=np.int32)  # Initialize distance field with INF
    dist[land] = 0  # Land tiles have distance 0; we propagate distances into water

    for y in range(h):  # Forward pass over rows
        row = dist[y]  # Reference to current row for speed
        up = dist[y - 1] if y > 0 else None  # Reference to previous row, if exists
        for x in range(w):  # Forward pass over columns
            best = row[x]  # Current best distance
            if up is not None:  # If we have an upper neighbor row
                best = min(best, up[x] + 1)  # Consider tile directly above
                if x > 0:  # If upper-left exists
                    best = min(best, up[x - 1] + 2)  # Consider upper-left diagonal (cost 2)
                if x + 1 < w:  # If upper-right exists
                    best = min(best, up[x + 1] + 2)  # Consider upper-right diagonal (cost 2)
            if x > 0:  # If left neighbor exists
                best = min(best, row[x - 1] + 1)  # Consider left neighbor (cost 1)
            row[x] = best  # Write updated distance

    for y in range(h - 1, -1, -1):  # Backward pass over rows
        row = dist[y]  # Current row
        dn = dist[y + 1] if y + 1 < h else None  # Next row down, if exists
        for x in range(w - 1, -1, -1):  # Backward pass over columns
            best = row[x]  # Current best
            if dn is not None:  # If we have a lower neighbor row
                best = min(best, dn[x] + 1)  # Consider tile directly below
                if x > 0:  # If lower-left exists
                    best = min(best, dn[x - 1] + 2)  # Consider lower-left diagonal
                if x + 1 < w:  # If lower-right exists
                    best = min(best, dn[x + 1] + 2)  # Consider lower-right diagonal
            if x + 1 < w:  # If right neighbor exists
                best = min(best, row[x + 1] + 1)  # Consider right neighbor
            row[x] = best  # Update distance

    return water & (dist <= int(band_pixels))  # Shallow ring: deep water within distance threshold


def place_decorators(
    biome: np.ndarray,  # biome code map
    rng: np.random.Generator,  # RNG for placement randomness
    densities: Dict[str, float],  # biome-name -> density (0..1-ish) map
    noise: np.ndarray,  # noise field used to bias distribution/clumping
) -> np.ndarray:
    # Generic decorator placement:
    # For each biome:
    # - compute a blended score from pure randomness and a noise field
    # - convert density into a threshold
    # - place decorator where score exceeds threshold

    h, w = biome.shape  # dimensions
    out = np.zeros((h, w), dtype=bool)  # output placement mask
    names = biome_names()  # code -> name map

    r = rng.random((h, w), dtype=np.float32)  # per-tile random values (unique each call/seed)
    for code, bname in names.items():  # iterate each biome type
        d = float(densities.get(bname, 0.0))  # density for this biome (default 0 means none)
        if d <= 0:  # skip biomes with no density
            continue  # next biome
        mask = (biome == code)  # tiles that are this biome
        if not np.any(mask):  # no tiles in this biome => skip
            continue  # next biome

        score = 0.55 * r + 0.45 * noise  # blend: randomness + structured noise (clumping)
        thresh = 1.0 - np.clip(d, 0.0, 0.95)  # map density to threshold (cap at 0.95 to avoid “all tiles”)
        out |= mask & (score >= thresh)  # set placements for this biome into output mask

    return out  # boolean mask where decorator should be placed


def place_ore_type(
    height: np.ndarray,  # heightmap for height constraints
    biome: np.ndarray,  # biome map for per-biome density
    rng: np.random.Generator,  # RNG for variation
    ore_cfg: dict,  # ore configuration entry (name, densities, height limits, etc.)
    clump_noise: np.ndarray,  # noise field controlling clustering
) -> np.ndarray:
    # Place one ore:
    # - restrict by min/max height
    # - for each biome, apply a biome-specific density threshold
    # - use clump noise to create vein-like clustering

    h, w = height.shape  # dimensions
    out = np.zeros((h, w), dtype=bool)  # output ore placement mask

    min_h = float(ore_cfg.get("min_height", 0.0))  # minimum height for this ore to appear
    max_h = float(ore_cfg.get("max_height", 1.01))  # maximum height (exclusive-ish)
    dens_map = ore_cfg.get("per_biome_density", {})  # per-biome density overrides

    valid_height = (height >= min_h) & (height < max_h)  # height constraint mask

    names = biome_names()  # code->name mapping
    r = rng.random((h, w), dtype=np.float32)  # random field for mixing with clump noise

    for code, bname in names.items():  # iterate biomes
        d = float(dens_map.get(bname, 0.0))  # density of this ore in this biome
        if d <= 0:  # if ore doesn’t spawn in this biome
            continue  # next biome
        bm = (biome == code)  # biome mask
        if not np.any(bm):  # skip if no tiles of this biome exist
            continue  # next biome

        thresh = 1.0 - np.clip(d, 0.0, 0.25)  # convert density to threshold (ore density capped lower than decorators)
        score = 0.65 * clump_noise + 0.35 * r  # more weight on clump noise => ore appears in clusters/veins
        out |= bm & valid_height & (score >= thresh)  # set ore placements

    return out  # return ore placement mask


def generate_world_data(config_path: str = CONFIG_PATH) -> Tuple[list, list]:
    # Main world generation pipeline:
    # 1) Read config and determine seed/dimensions
    # 2) Generate height/moisture/temp noise
    # 3) Shape height into an island using radial mask
    # 4) Classify biomes from rule list + sea level
    # 5) Add shallow-water band near coasts
    # 6) Place decorators (trees/bushes/grass)
    # 7) Place ores
    # 8) Emit world_tiles and object_tiles in list-of-list dict format

    cfg = load_config(config_path)  # Load config dictionary

    W = int(cfg["window"]["width"])  # Map width in tiles
    H = int(cfg["window"]["height"])  # Map height in tiles

    gen = cfg["generation"]  # Convenience alias to generation sub-config
    seed = gen.get("seed", None)  # Get seed if specified
    if seed is None:  # If no seed specified
        seed = int(time.time() * 1000) & 0xFFFFFFFF  # Create time-based seed (32-bit)
    seed = int(seed)  # Ensure seed is int

    rng = np.random.default_rng(seed)  # Main RNG seeded deterministically for reproducibility

    octaves = int(gen["octaves"])  # Number of noise octaves
    persistence = float(gen["persistence"])  # Amplitude decay per octave
    lacunarity = float(gen["lacunarity"])  # Frequency growth per octave

    island = gen["island"]  # Island shaping sub-config
    radius = float(island["radius"])  # Radius controlling island size
    edge_falloff = float(island["edge_falloff"])  # Controls shoreline steepness
    center_jitter = float(island["center_jitter"])  # Random center offset

    sea_level = float(gen["sea_level"])  # Sea level threshold for deep water

    base_grid = max(24, min(W, H) // 6)  # Base grid size used for noise; ties scale to map size

    height_noise = normalize01(  # Normalize height noise to 0..1
        fbm_noise(W, H, base_grid, octaves, persistence, lacunarity, rng)  # Multi-octave noise for terrain
    )  # End normalize
    moisture = normalize01(  # Normalize moisture map
        fbm_noise(W, H, base_grid, max(3, octaves - 1), persistence, lacunarity, rng)  # Slightly fewer octaves
    )  # End normalize
    temp = normalize01(  # Normalize temperature map
        fbm_noise(W, H, base_grid, max(3, octaves - 1), persistence, lacunarity, rng)  # Slightly fewer octaves
    )  # End normalize

    mask = island_mask(W, H, radius, edge_falloff, center_jitter, rng)  # Radial mask making land concentrate near center

    heightmap = normalize01(0.70 * height_noise + 0.30 * mask)  # Mix base terrain with island mask
    heightmap = heightmap * (0.30 + 0.70 * mask)  # Further suppress edges so oceans dominate around perimeter
    heightmap = normalize01(heightmap)  # Re-normalize after shaping

    rules = cfg["biomes"].get("rules", [])  # Biome classification rules list
    biome = classify_biomes_from_rules(heightmap, moisture, temp, sea_level, rules)  # Produce biome codes map

    shallow_cfg = gen.get("shallow_water", {})  # Shallow-water config (optional)
    if shallow_cfg.get("enabled", True):  # If shallow water band is enabled (default True)
        band = int(shallow_cfg.get("band_pixels", 14))  # Width of shallow ring in pixels/tiles
        shallow = compute_shallow_ring(biome, band_pixels=band)  # Compute shallow ring mask
        biome[shallow] = biome_codes()["shallow_water"]  # Replace deep water with shallow water in that band

    rng_dec = np.random.default_rng(  # Create a second RNG for decoration placement
        (seed ^ (int(time.time() * 1000) & 0xFFFFFFFF)) & 0xFFFFFFFF  # Seed mixed with current time for variety
    )  # End RNG creation
    decorator_noise = normalize01(  # Normalize decorator noise field
        value_noise_2d(W, H, grid=max(12, min(W, H) // 10), rng=rng_dec)  # Lower frequency noise for clustering
    )  # End normalize

    dec = cfg.get("decorators", {})  # Decorators config section
    trees_mask = np.zeros((H, W), dtype=bool)  # Where trees should be placed
    bushes_mask = np.zeros((H, W), dtype=bool)  # Where bushes should be placed
    grass_mask = np.zeros((H, W), dtype=bool)  # Where grass should be placed

    if dec.get("trees", {}).get("enabled", True):  # If trees decorator enabled
        tdens = dec["trees"].get("per_biome_density", {})  # Per-biome tree density map
        trees_mask = place_decorators(biome, rng_dec, tdens, decorator_noise)  # Compute placement mask

    if dec.get("bushes", {}).get("enabled", True):  # If bushes decorator enabled
        bdens = dec["bushes"].get("per_biome_density", {})  # Per-biome bush density map
        bushes_mask = place_decorators(biome, rng_dec, bdens, decorator_noise)  # Compute placement mask

    if dec.get("grass", {}).get("enabled", True):  # If grass decorator enabled
        gdens = dec["grass"].get("per_biome_density", {})  # Per-biome grass density map
        grass_mask = place_decorators(biome, rng_dec, gdens, decorator_noise)  # Compute placement mask

    ores_cfg = cfg.get("ores", {})  # Ores config section
    ore_masks: Dict[str, np.ndarray] = {}  # Map ore name -> placement mask
    if ores_cfg.get("enabled", True):  # If ores enabled
        ng = int(ores_cfg.get("clumping", {}).get("noise_grid", 10))  # Clump noise grid size parameter
        ore_noise = normalize01(  # Normalize ore clump noise
            value_noise_2d(W, H, grid=max(6, ng), rng=rng_dec)  # Generate clump noise at chosen frequency
        )  # End normalize
        for ore in ores_cfg.get("types", []):  # Iterate ore definitions
            ore_name = str(ore.get("name", "ore"))  # Ore type name (default "ore" if missing)
            ore_masks[ore_name] = place_ore_type(heightmap, biome, rng_dec, ore, ore_noise)  # Place ore type

    name_map = biome_names()  # Code->name mapping used for output tiles

    world_tiles: List[List[dict]] = []  # Output grid (rows) of biome tile dicts
    object_tiles: List[List[dict]] = []  # Output grid (rows) of object tile dicts

    obj_type = np.full((H, W), None, dtype=object)  # Per-tile object type string (or None)

    obj_type[grass_mask] = "grass"  # Assign grass objects to tiles in grass_mask
    obj_type[bushes_mask] = "bush"  # Assign bush objects (overwrites grass if overlapping)
    obj_type[trees_mask] = "tree"  # Assign tree objects (overwrites bush/grass if overlapping)
    for ore_name, m in ore_masks.items():  # Assign ore objects for each ore type
        obj_type[m] = ore_name  # Ores overwrite any prior decorator where they overlap

    for y in range(H):  # Build output row by row
        wrow = []  # Biome row list
        orow = []  # Object row list
        for x in range(W):  # Build each tile in the row
            wrow.append({"pos": (x, y), "type": name_map[int(biome[y, x])]})  # Store position + biome name
            t = obj_type[y, x]  # Get object type at this tile
            orow.append({"pos": (x, y), "type": None if t is None else str(t)})  # Store position + object type
        world_tiles.append(wrow)  # Add completed biome row
        object_tiles.append(orow)  # Add completed object row

    deep = biome_codes()["deep_water"]  # Deep water code
    non_sea = int(np.count_nonzero(biome != deep))  # Count all tiles that are not deep water (land + shallow)
    print(f"[WORLD] seed={seed} size={W}x{H} non-sea-tiles={non_sea}")  # Debug summary line

    return world_tiles, object_tiles  # Return both grids for use by the game
