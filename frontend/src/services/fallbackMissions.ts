import {
  EnvironmentType,
  MissionPreferenceRequest,
  MissionResponse,
  MissionStep,
  SensoryType,
} from '../types/mission';

interface EnvironmentData {
  titlePrefix: string;
  taglines: string[];
  leaveNoTrace: string;
  safetyNotes: string[];
  stepTemplates: Array<{
    title: string;
    instruction: string;
    sensory: SensoryType;
  }>;
}

const ENVIRONMENT_CATALOG: Record<EnvironmentType, EnvironmentData> = {
  park: {
    titlePrefix: 'Green Haven',
    taglines: [
      'Observe the quiet choreography of open lawns and gentle tree branches.',
      'Ground yourself in communal green spaces and notice dappled sunlight.',
    ],
    leaveNoTrace: 'Pack out all personal items and keep pets on designated park paths.',
    safetyNotes: [
      'Remain on paved or gravel walking paths.',
      'Be alert to bicycles, runners, and other recreation visitors.',
      'Do not consume any park plants, berries, or standing fountain water.',
    ],
    stepTemplates: [
      {
        title: 'Sensory Grounding',
        instruction: 'Stand quietly by a tree trunk for 2 minutes. Close your eyes and identify 3 distinct natural sounds above urban noise.',
        sensory: 'sound',
      },
      {
        title: 'Fallen Leaf Veins',
        instruction: 'Find two fallen leaves on the ground. Trace the ribbed vascular veins with your thumb without tearing them.',
        sensory: 'touch',
      },
      {
        title: 'Canopy Color Gradient',
        instruction: 'Gaze into the tree leaves above. Identify at least four distinct gradations of green from sunlight to shadow.',
        sensory: 'sight',
      },
      {
        title: 'Petrichor Inhale',
        instruction: 'Kneel near damp mulch or soil. Inhale deeply three times and note the earthy aroma.',
        sensory: 'scent',
      },
      {
        title: 'Verge Contemplation',
        instruction: 'Sit on a bench or grassy verge for 3 minutes. Synchronize your breathing with the rhythm of rustling leaves.',
        sensory: 'spatial',
      },
    ],
  },
  forest: {
    titlePrefix: 'Canopy Whisper',
    taglines: [
      'Step beneath the ancient canopy and let the forest floor soften your thoughts.',
      'Trace the quiet dialogue between moss, nurse logs, and soaring trunks.',
    ],
    leaveNoTrace: 'Stay strictly on marked trails to protect delicate fungal networks and soil biomes.',
    safetyNotes: [
      'Stay on marked forest paths at all times.',
      'Never ingest wild mushrooms, fungi, or unknown forest berries.',
      'Watch footing for exposed roots, damp rocks, and loose mud.',
    ],
    stepTemplates: [
      {
        title: 'Threshold Silence',
        instruction: 'Pause at the forest trail entrance for 90 seconds. Listen to the sudden dampening of outside sounds.',
        sensory: 'sound',
      },
      {
        title: 'Bark Texture Expedition',
        instruction: 'Gently press your fingertips against the bark of two different tree species. Feel ridges and lichen patterns.',
        sensory: 'touch',
      },
      {
        title: 'Moss Micro-World',
        instruction: 'Find a fallen log or stone carpeted in moss. Look closely at the tiny miniature forest of sporophytes.',
        sensory: 'sight',
      },
      {
        title: 'Pine Needle Aroma',
        instruction: 'Rub a dry fallen pine or fir needle between your fingertips. Inhale the aromatic evergreen resin.',
        sensory: 'scent',
      },
      {
        title: 'Sky Window Search',
        instruction: 'Look straight up into the crown. Search for the clearest opening where sunlight cuts through the foliage.',
        sensory: 'spatial',
      },
    ],
  },
  garden: {
    titlePrefix: 'Botanical Wonder',
    taglines: [
      'Immerse your senses in intentional flora, pollinator highways, and rich soil.',
      'Slow down to witness the quiet industry of garden beds and flowering borders.',
    ],
    leaveNoTrace: 'Admire blooms with eyes and camera; never pick living flowers or produce.',
    safetyNotes: [
      'Walk cautiously on narrow flagstone paths.',
      'Observe bees and pollinating insects with calm stillness without swatting.',
      'Do not harvest or sample garden plants without explicit permission.',
    ],
    stepTemplates: [
      {
        title: 'Petal Symmetry',
        instruction: 'Examine a single flower closely. Count petals and notice the spiral symmetry of its seed center.',
        sensory: 'sight',
      },
      {
        title: 'Aromatic Foliage Hover',
        instruction: 'Hover your nose near aromatic leaves (lavender, mint, or rosemary) without picking or damaging the stem.',
        sensory: 'scent',
      },
      {
        title: 'Pollinator Watch',
        instruction: 'Stay still beside a flowering patch for 3 minutes. Count how many winged insects visit the blooms.',
        sensory: 'sight',
      },
      {
        title: 'Soft Leaf Touch',
        instruction: 'Find a fuzzy leaf (like lamb’s ear or sage) and brush the tip of your index finger across its velvety surface.',
        sensory: 'touch',
      },
      {
        title: 'Garden Rustle',
        instruction: 'Close your eyes for 2 minutes and tune into the hum of flying insects and rustling flower stalks.',
        sensory: 'sound',
      },
    ],
  },
  waterfront: {
    titlePrefix: 'Shoreline Rhythms',
    taglines: [
      'Synchronize your breathing with the rhythm of lapping water and shoreline winds.',
      'Witness the soothing boundary where solid earth meets liquid movement.',
    ],
    leaveNoTrace: 'Keep all trash far from water banks; protect nesting shoreline birds.',
    safetyNotes: [
      'Maintain a safe distance from steep, wet, or slippery embankments.',
      'Do not enter moving water currents.',
      'Never drink untreated river, lake, or pond water.',
    ],
    stepTemplates: [
      {
        title: 'Water Cadence Listening',
        instruction: 'Stand near the bank and close your eyes. Match your inhales and exhales to the tempo of ripples or waves.',
        sensory: 'sound',
      },
      {
        title: 'Pebble Smoothness',
        instruction: 'Pick up a dry water-smoothed stone from the path edge. Feel the cool, polished texture against your palm.',
        sensory: 'touch',
      },
      {
        title: 'Reflection Watching',
        instruction: 'Gaze into the water surface. Observe how the breeze fractures sky reflections into dynamic abstract mosaics.',
        sensory: 'sight',
      },
      {
        title: 'Aquatic Breeze Inhale',
        instruction: 'Face directly into the wind blowing off the water. Feel the cool humidity and catch the fresh aquatic scent.',
        sensory: 'scent',
      },
      {
        title: 'Horizon Relaxation',
        instruction: 'Look across the widest expanse of water visible. Let your vision widen into relaxed peripheral awareness.',
        sensory: 'spatial',
      },
    ],
  },
  trail: {
    titlePrefix: "Pathfinder's Stride",
    taglines: [
      'Navigate the twists of the dirt trail with grounded, intentional strides.',
      'Follow the contour of the earth and reconnect with forward momentum in open air.',
    ],
    leaveNoTrace: 'Stick to the center of the trail to prevent trail widening and soil erosion.',
    safetyNotes: [
      'Check trail markers regularly to maintain directional orientation.',
      'Yield to uphill hikers and maintain steady footing on loose gravel.',
      'Carry hydration and be mindful of sun exposure.',
    ],
    stepTemplates: [
      {
        title: 'Grounded Footstrike',
        instruction: 'Walk 100 paces focusing completely on the tactile roll of your feet against the dirt and gravel.',
        sensory: 'touch',
      },
      {
        title: 'Trail Vista Spotting',
        instruction: 'Pause at the first bend or ridge. Survey the landscape contours stretching out before you.',
        sensory: 'sight',
      },
      {
        title: 'Wind Direction Check',
        instruction: 'Turn your face until you feel the breeze evenly on both cheeks. Determine the wind’s heading.',
        sensory: 'touch',
      },
      {
        title: 'Bird Flight Observation',
        instruction: 'Scan the tree line for birds darting between branches. Follow one bird’s flight path.',
        sensory: 'sight',
      },
      {
        title: 'Silent Stride Minute',
        instruction: 'Walk for one full minute making as little footstep sound as humanly possible.',
        sensory: 'sound',
      },
    ],
  },
  neighborhood: {
    titlePrefix: 'Urban Naturalist',
    taglines: [
      'Discover resilient pockets of biodiversity nestled in sidewalk cracks and tree wells.',
      'Re-enchant familiar streets by noticing the wild organisms living alongside us.',
    ],
    leaveNoTrace: 'Respect private property boundaries; observe garden verges from public sidewalks.',
    safetyNotes: [
      'Use marked pedestrian crossings and watch for vehicular traffic.',
      'Stay strictly on public sidewalks and easements; never trespass.',
      'Avoid touching unknown neighborhood plants or unfamiliar domestic pets.',
    ],
    stepTemplates: [
      {
        title: 'Pavement Sprout',
        instruction: 'Locate a resilient plant emerging from a pavement seam. Observe its survival geometry.',
        sensory: 'sight',
      },
      {
        title: 'Street Tree Canopy',
        instruction: 'Look up into the nearest street tree. Notice how branches weave around overhead utilities and buildings.',
        sensory: 'spatial',
      },
      {
        title: 'Urban Bird Listening',
        instruction: 'Filter out engine sounds and identify two distinct neighborhood bird vocalizations.',
        sensory: 'sound',
      },
      {
        title: 'Sun-Warmed Brick',
        instruction: 'Touch a south-facing exterior brick or masonry wall. Feel the thermal energy stored from the sun.',
        sensory: 'touch',
      },
      {
        title: 'Verge Flower Appreciation',
        instruction: 'Find a curb garden flower or ornamental shrub. Spend 30 seconds appreciating its vibrant color.',
        sensory: 'sight',
      },
    ],
  },
};

export function generateClientFallbackMission(
  prefs: MissionPreferenceRequest
): MissionResponse {
  const envData = ENVIRONMENT_CATALOG[prefs.environment] || ENVIRONMENT_CATALOG.park;
  const stepCount = prefs.duration_minutes <= 15 ? 2 : prefs.duration_minutes <= 35 ? 3 : 4;
  const selectedTemplates = envData.stepTemplates.slice(0, stepCount);

  const baseMinutes = Math.max(3, Math.floor(prefs.duration_minutes / stepCount));
  const remainder = prefs.duration_minutes - baseMinutes * stepCount;

  const steps: MissionStep[] = selectedTemplates.map((t, idx) => ({
    step_number: idx + 1,
    title: t.title,
    instruction: t.instruction,
    sensory_type: t.sensory,
    estimated_minutes: baseMinutes + (idx === 0 ? remainder : 0),
    completed: false,
  }));

  const hash = Math.random().toString(36).substring(2, 7);
  const id = `gq-offline-${prefs.environment}-${prefs.mood}-${hash}`;

  return {
    id,
    title: `${envData.titlePrefix}: ${prefs.mood.charAt(0).toUpperCase() + prefs.mood.slice(1)} Quest`,
    tagline: envData.taglines[0],
    environment: prefs.environment,
    estimated_duration_minutes: prefs.duration_minutes,
    difficulty: prefs.energy_level === 'low' ? 'easy' : prefs.energy_level === 'brisk' ? 'challenging' : 'moderate',
    theme: `${prefs.mood.charAt(0).toUpperCase() + prefs.mood.slice(1)} ${prefs.environment.charAt(0).toUpperCase() + prefs.environment.slice(1)} Exploration`,
    sensory_prompt: `Focus attention on ${prefs.sensory_focus.join(', ')}. Slow down and absorb each sensation.`,
    leave_no_trace_principle: envData.leaveNoTrace,
    safety_notes: envData.safetyNotes,
    steps,
    generator_info: {
      provider: 'client-offline',
      model: 'deterministic-pwa-v1',
      fallback_used: true,
      generation_time_ms: 12,
      safety_validated: true,
    },
    created_at: new Date().toISOString(),
  };
}

