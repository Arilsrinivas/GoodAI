"use client";

import {
  Clapperboard,
  FileText,
  Play,
  Upload,
  Loader2,
  Sparkles,
  Film,
  Download,
  Sliders,
  X,
  Copy,
  Check,
  Camera,
  Music,
  Volume2,
  Users,
  MapPin,
  ListVideo,
  FolderOpen,
  Wand2,
  ChevronRight,
  Zap,
} from "lucide-react";
import { useState, useEffect, useRef, DragEvent, ChangeEvent } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type VisualMemory = {
  camera: string;
  lens: string;
  lighting: string;
  weather?: string;
  color_grading: string;
  time_of_day?: string;
  composition: string;
  character_positions?: Record<string, string>;
  object_positions?: Record<string, string>;
  environment?: string;
  style: string;
};

type Shot = {
  id: string;
  scene_order: number;
  shot_number: number;
  shot_type: string;
  camera_movement: string;
  summary: string;
  prompt: string;
  duration_seconds: number;
};

type SoundEffectBeat = {
  id: string;
  scene_order: number;
  category: string;
  description: string;
  timing_seconds: number;
};

type BackgroundMusicTrack = {
  id: string;
  scene_order: number;
  mood: string;
  genre: string;
  tempo: string;
  intensity: number;
  transition_point?: string;
};

type VoiceScript = {
  id: string;
  scene_order: number;
  speaker: string;
  text: string;
  ssml_text: string;
  voice_emotion: string;
  speech_speed: string;
  pauses?: string;
};

type CharacterMemory = {
  id: string;
  name: string;
  aliases?: string[];
  age?: string;
  gender?: string;
  height?: string;
  body_type?: string;
  face_shape?: string;
  eye_colour?: string;
  eyes?: string;
  hair?: string;
  hairstyle?: string;
  skin_tone?: string;
  face?: string;
  clothing?: string;
  accessories?: string[];
  voice?: string;
  personality?: string[];
  power_level?: string;
  abilities?: string[];
  master_reference_image_url?: string;
};

type LocationMemory = {
  id: string;
  name: string;
  architecture?: string;
  lighting?: string;
  weather?: string;
  season?: string;
  time_of_day?: string;
  environment?: string;
  textures?: string;
  vegetation?: string;
  props?: string[];
  colour_palette?: string;
};

type Scene = {
  id: string;
  order: number;
  title: string;
  opening_frame: string;
  ending_frame: string;
  narration: string;
  prompt: string;
  negative_prompt: string;
  duration_seconds: number;
  objects?: string[];
  characters?: string[];
  environment?: string;
  camera: string;
  transitions: string;
  visual_memory?: VisualMemory;
  shots?: Shot[];
  sfx?: SoundEffectBeat[];
  music?: BackgroundMusicTrack[];
  voice?: VoiceScript[];
};

type StoryPlan = {
  id: string;
  title: string;
  created_at?: string;
  scenes: Scene[];
  characters?: CharacterMemory[];
  locations?: LocationMemory[];
  shots?: Shot[];
  sfx_plan?: SoundEffectBeat[];
  music_plan?: BackgroundMusicTrack[];
  voice_script?: VoiceScript[];
  qa_report: { passed: boolean };
};

type VideoSceneAsset = {
  scene_id: string;
  order: number;
  provider: string;
  status: string;
  video_path?: string;
  final_frame_path?: string;
  reference_frame_path?: string;
  error?: string;
};

type MovieExport = {
  plan_id: string;
  status: string;
  export_dir: string;
  final_movie_path?: string;
  video_assets: VideoSceneAsset[];
  warnings?: string[];
};

type TabType =
  | "new_project"
  | "saved_projects"
  | "storyboard"
  | "characters"
  | "locations"
  | "audio_studio"
  | "render_queue"
  | "export_hub";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabType>("new_project");

  const [title, setTitle] = useState("The Hidden Power");
  const [text, setText] = useState(
    "Chapter 1: The Awakening\n\nKael stood at the edge of the Obsidian Rift, his glowing crimson talisman humming with suppressed power. Across the stormy chasm, Nova channeled blue ether energy, preparing for the clash that would decide the fate of the realm."
  );
  const [videoStyle, setVideoStyle] = useState("realistic_cinema");
  const [narrationStyle, setNarrationStyle] = useState("storytelling");
  const [targetModel, setTargetModel] = useState("bytedance/seedance-2.0-mini/text-to-video");

  const [inputMode, setInputMode] = useState<"text" | "upload">("text");
  const [fileData, setFileData] = useState<{ name: string; size: number; base64: string } | null>(null);

  const [plan, setPlan] = useState<StoryPlan | null>(null);
  const [savedPlans, setSavedPlans] = useState<StoryPlan[]>([]);
  const [movieExport, setMovieExport] = useState<MovieExport | null>(null);
  const [status, setStatus] = useState("Ready");
  const [isLoading, setIsLoading] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedScene, setSelectedScene] = useState<Scene | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  useEffect(() => {
    fetchSavedProjects();
  }, []);

  const fetchSavedProjects = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/story-jobs`);
      if (res.ok) {
        const data = await res.json();
        setSavedPlans(data);
      }
    } catch (e) {
      console.warn("Could not fetch saved projects:", e);
    }
  };

  const copyToClipboard = (content: string, key: string) => {
    navigator.clipboard.writeText(content);
    setCopiedText(key);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const videoStyles = [
    { value: "realistic_cinema", label: "Realistic Cinema 4K" },
    { value: "photorealistic", label: "Photorealistic" },
    { value: "pixar", label: "Pixar 3D Animation" },
    { value: "anime", label: "Anime / Cel Shaded" },
    { value: "studio_ghibli", label: "Studio Ghibli" },
    { value: "comic", label: "Comic Book / Graphic Novel" },
    { value: "vintage", label: "35mm Vintage Film" },
    { value: "documentary", label: "Documentary Realism" },
  ];

  const narrationStyles = [
    { value: "storytelling", label: "Classic Storytelling" },
    { value: "documentary", label: "Documentary Narrator" },
    { value: "historical", label: "Epic Historical Narrator" },
    { value: "movie_trailer", label: "Movie Trailer Voice" },
    { value: "fantasy", label: "Fantasy Tale Narrator" },
  ];

  const targetModels = [
    { value: "bytedance/seedance-2.0-mini/text-to-video", label: "Seedance 2.0 Mini (AtlasCloud - Fast & Efficient)" },
    { value: "minimax/h3-developer/text-to-video", label: "MiniMax H3 Developer (AtlasCloud)" },
    { value: "bytedance/seedance-v1.5-pro/text-to-video", label: "Seedance v1.5 Pro (AtlasCloud)" },
    { value: "kwaivgi/kling-v2.6-pro/text-to-video", label: "Kling v2.6 Pro (AtlasCloud)" },
    { value: "minimax/hailuo-2.3/t2v-standard", label: "Hailuo 2.3 Standard (AtlasCloud)" },
    { value: "alibaba/wan-2.6/text-to-video", label: "Wan 2.6 (AtlasCloud)" },
  ];

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const processFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      if (event.target?.result) {
        const dataUrl = event.target.result as string;
        const base64Str = dataUrl.split(",")[1];
        setFileData({
          name: file.name,
          size: file.size,
          base64: base64Str,
        });
        if (!title || title === "The Hidden Power") {
          const cleanName = file.name.substring(0, file.name.lastIndexOf(".")) || file.name;
          setTitle(cleanName);
        }
      }
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  async function analyzeStory() {
    setIsLoading(true);
    setStatus("Analyzing story with AI Director...");
    setPlan(null);
    setMovieExport(null);

    try {
      let response;
      if (inputMode === "text") {
        response = await fetch(`${API_BASE_URL}/api/v1/story-jobs/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title,
            text,
            video_style: videoStyle,
            narration_style: narrationStyle,
            target_model: targetModel,
          }),
        });
      } else {
        if (!fileData) {
          alert("Please upload a document file first.");
          setIsLoading(false);
          setStatus("Ready");
          return;
        }
        response = await fetch(`${API_BASE_URL}/api/v1/story-jobs/analyze-document`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            filename: fileData.name,
            content_base64: fileData.base64,
            title,
            video_style: videoStyle,
            narration_style: narrationStyle,
            target_model: targetModel,
          }),
        });
      }

      if (!response.ok) {
        let errDetail = "Analysis failed";
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            errDetail = typeof errData.detail === "string" ? errData.detail : JSON.stringify(errData.detail);
          }
        } catch {}
        setStatus(`Error: ${errDetail}`);
        throw new Error(errDetail);
      }

      const data = (await response.json()) as StoryPlan;
      setPlan(data);
      setStatus("Director plan generated");
      setActiveTab("storyboard");
      fetchSavedProjects();
    } catch (err) {
      console.error(err);
      setStatus("Analysis failed");
    } finally {
      setIsLoading(false);
    }
  }

  async function pollExportStatus(planId: string) {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/story-jobs/${planId}/export`);
        if (res.ok) {
          const exportData = (await res.json()) as MovieExport;
          setMovieExport(exportData);
          if (exportData.status === "completed" || exportData.status === "failed" || exportData.status === "skipped") {
            setIsExporting(false);
            setStatus(`Video Export ${exportData.status}`);
            clearInterval(interval);
          }
        }
      } catch (e) {
        console.warn("Polling export status error:", e);
      }
    }, 3000);
  }

  async function triggerVideoExport() {
    if (!plan) return;
    setIsExporting(true);
    setStatus("Generating background video export...");
    setActiveTab("render_queue");

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/story-jobs/${plan.id}/generate-videos`, {
        method: "POST",
      });

      if (!response.ok) {
        setStatus("Failed to start video export");
        setIsExporting(false);
        return;
      }

      const initialExport = (await response.json()) as MovieExport;
      setMovieExport(initialExport);
      pollExportStatus(plan.id);
    } catch (err) {
      console.error(err);
      setStatus("Export request failed");
      setIsExporting(false);
    }
  }

  const completedAssetsCount = movieExport?.video_assets?.filter((a) => a.status === "completed").length || 0;
  const totalAssetsCount = plan?.scenes?.length || movieExport?.video_assets?.length || 0;
  const progressPercent = totalAssetsCount > 0 ? Math.round((completedAssetsCount / totalAssetsCount) * 100) : 0;

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans selection:bg-amber-500 selection:text-black">
      {/* Wix Studio-Style Sticky Top Navigation Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-zinc-950/80 border-b border-zinc-800/80 px-6 py-3.5 flex items-center justify-between shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 via-purple-600 to-indigo-500 p-0.5 shadow-lg shadow-amber-500/20">
            <div className="w-full h-full bg-zinc-950 rounded-[10px] flex items-center justify-center">
              <Clapperboard className="w-5 h-5 text-amber-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-lg tracking-tight text-white">Cinematic AI Studio</h1>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                PRO ENGINE
              </span>
            </div>
            <p className="text-xs text-zinc-400">Hidden Power Story-to-Movie Pipeline</p>
          </div>
        </div>

        {/* Studio Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-zinc-900/90 p-1.5 rounded-xl border border-zinc-800">
          {[
            { id: "new_project", label: "New Project", icon: Sparkles },
            { id: "saved_projects", label: "Projects", icon: FolderOpen, badge: savedPlans.length },
            { id: "storyboard", label: "Shot Board", icon: ListVideo, disabled: !plan },
            { id: "characters", label: "Characters", icon: Users, disabled: !plan },
            { id: "locations", label: "Locations", icon: MapPin, disabled: !plan },
            { id: "audio_studio", label: "Audio & SSML", icon: Volume2, disabled: !plan },
            { id: "render_queue", label: "Render Queue", icon: Film, disabled: !plan },
            { id: "export_hub", label: "Export Hub", icon: Download, disabled: !plan },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                disabled={tab.disabled}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  tab.disabled ? "opacity-40 cursor-not-allowed text-zinc-500" : "hover:text-white"
                } ${
                  isActive
                    ? "bg-gradient-to-r from-amber-500 to-amber-600 text-black font-semibold shadow-md shadow-amber-500/20"
                    : "text-zinc-400 hover:bg-zinc-800/60"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
                {tab.badge !== undefined && tab.badge > 0 && (
                  <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isActive ? "bg-black/20 text-black" : "bg-zinc-800 text-zinc-300"}`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Action Button */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-xs text-zinc-400 bg-zinc-900/80 px-3 py-1.5 rounded-lg border border-zinc-800">
            <span className={`w-2 h-2 rounded-full ${isLoading || isExporting ? "bg-amber-400 animate-pulse" : "bg-emerald-400"}`} />
            <span>{status}</span>
          </div>
          {plan && (
            <button
              onClick={triggerVideoExport}
              disabled={isExporting}
              className="flex items-center space-x-1.5 bg-gradient-to-r from-amber-500 via-orange-500 to-amber-600 hover:from-amber-400 hover:to-orange-500 text-black font-semibold text-xs px-4 py-2 rounded-xl shadow-lg shadow-amber-500/20 transition-all transform active:scale-95 disabled:opacity-50"
            >
              {isExporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              <span>Render Movie</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="p-8 max-w-7xl mx-auto">
        {/* TAB 1: NEW PROJECT & STORY INPUT */}
        {activeTab === "new_project" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-zinc-900/60 backdrop-blur-xl border border-zinc-800/80 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                      <FileText className="w-5 h-5 text-amber-400" />
                    </div>
                    <div>
                      <h2 className="text-lg font-bold text-white">Story Ingestion Engine</h2>
                      <p className="text-xs text-zinc-400">Accepts plain text, PDF, DOCX, Markdown, EPUB, & Fountain scripts</p>
                    </div>
                  </div>

                  {/* Input Mode Switcher */}
                  <div className="flex items-center bg-zinc-950 p-1 rounded-xl border border-zinc-800 text-xs">
                    <button
                      onClick={() => setInputMode("text")}
                      className={`px-3 py-1 rounded-lg transition-all ${
                        inputMode === "text" ? "bg-amber-500 text-black font-semibold shadow" : "text-zinc-400 hover:text-white"
                      }`}
                    >
                      Paste Story
                    </button>
                    <button
                      onClick={() => setInputMode("upload")}
                      className={`px-3 py-1 rounded-lg transition-all ${
                        inputMode === "upload" ? "bg-amber-500 text-black font-semibold shadow" : "text-zinc-400 hover:text-white"
                      }`}
                    >
                      Upload File
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                      Project Title
                    </label>
                    <input
                      type="text"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="e.g. The Hidden Power"
                      className="w-full bg-zinc-950/80 border border-zinc-800 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-amber-500/50 transition-all"
                    />
                  </div>

                  {inputMode === "text" ? (
                    <div>
                      <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                        Story Narrative Text / Script
                      </label>
                      <textarea
                        rows={8}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste your story text or novel chapter here..."
                        className="w-full bg-zinc-950/80 border border-zinc-800 rounded-xl p-4 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-amber-500/50 transition-all leading-relaxed"
                      />
                    </div>
                  ) : (
                    <div>
                      <label className="block text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2">
                        Document File Upload
                      </label>
                      <div
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                          dragActive
                            ? "border-amber-500 bg-amber-500/10"
                            : fileData
                            ? "border-emerald-500/50 bg-emerald-500/5"
                            : "border-zinc-800 hover:border-zinc-700 bg-zinc-950/40"
                        }`}
                      >
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept=".pdf,.docx,.txt,.epub,.md,.markdown,.html,.fountain"
                          onChange={handleFileChange}
                          className="hidden"
                        />
                        <Upload className="w-10 h-10 mx-auto mb-3 text-zinc-500" />
                        {fileData ? (
                          <div className="space-y-1">
                            <p className="text-sm font-semibold text-emerald-400">{fileData.name}</p>
                            <p className="text-xs text-zinc-500">{(fileData.size / 1024).toFixed(1)} KB uploaded</p>
                          </div>
                        ) : (
                          <div className="space-y-1">
                            <p className="text-sm font-medium text-zinc-300">Drag & drop your story file here, or click to browse</p>
                            <p className="text-xs text-zinc-500">Supports PDF, DOCX, TXT, EPUB, MD, Fountain Script</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Sidebar Studio Settings */}
            <div className="space-y-6">
              <div className="bg-zinc-900/60 backdrop-blur-xl border border-zinc-800/80 rounded-2xl p-6 shadow-2xl space-y-5">
                <div className="flex items-center space-x-2 border-b border-zinc-800 pb-3">
                  <Sliders className="w-4 h-4 text-amber-400" />
                  <h3 className="font-bold text-sm text-white">Director Presets</h3>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-400 mb-1.5">Cinematic Visual Style</label>
                  <select
                    value={videoStyle}
                    onChange={(e) => setVideoStyle(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2.5 text-xs text-zinc-200 focus:outline-none focus:border-amber-500/50"
                  >
                    {videoStyles.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-400 mb-1.5">Narration Voice Style</label>
                  <select
                    value={narrationStyle}
                    onChange={(e) => setNarrationStyle(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2.5 text-xs text-zinc-200 focus:outline-none focus:border-amber-500/50"
                  >
                    {narrationStyles.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-400 mb-1.5">Target AI Video Generator</label>
                  <select
                    value={targetModel}
                    onChange={(e) => setTargetModel(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2.5 text-xs text-zinc-200 focus:outline-none focus:border-amber-500/50"
                  >
                    {targetModels.map((m) => (
                      <option key={m.value} value={m.value}>
                        {m.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="pt-2">
                  <button
                    onClick={analyzeStory}
                    disabled={isLoading}
                    className="w-full py-3.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 hover:from-amber-400 hover:to-amber-600 text-black font-bold text-sm shadow-xl shadow-amber-500/20 flex items-center justify-center space-x-2 transition-all transform active:scale-95 disabled:opacity-50"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Planning Movie...</span>
                      </>
                    ) : (
                      <>
                        <Wand2 className="w-5 h-5 fill-current" />
                        <span>Generate Director Plan</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SAVED PROJECTS GALLERY */}
        {activeTab === "saved_projects" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">Saved Film Projects</h2>
                <p className="text-xs text-zinc-400">Select any project to inspect storyboard, character bible, or export</p>
              </div>
              <button
                onClick={() => setActiveTab("new_project")}
                className="flex items-center space-x-1.5 text-xs bg-amber-500 text-black font-semibold px-4 py-2 rounded-xl hover:bg-amber-400 transition"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>New Story</span>
              </button>
            </div>

            {savedPlans.length === 0 ? (
              <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-2xl p-12 text-center">
                <FolderOpen className="w-12 h-12 mx-auto text-zinc-600 mb-3" />
                <p className="text-sm font-medium text-zinc-300">No saved projects found</p>
                <p className="text-xs text-zinc-500 mt-1">Create a new project using the Story Ingestion engine.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {savedPlans.map((p) => (
                  <div
                    key={p.id}
                    onClick={() => {
                      setPlan(p);
                      setActiveTab("storyboard");
                    }}
                    className={`bg-zinc-900/60 backdrop-blur-xl border rounded-2xl p-6 cursor-pointer hover:border-amber-500/50 hover:shadow-xl hover:shadow-amber-500/10 transition-all ${
                      plan?.id === p.id ? "border-amber-500 bg-amber-500/5" : "border-zinc-800/80"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-2 bg-amber-500/10 rounded-lg">
                        <Clapperboard className="w-5 h-5 text-amber-400" />
                      </div>
                      <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-zinc-800 text-zinc-300">
                        {p.scenes?.length || 0} Scenes
                      </span>
                    </div>

                    <h3 className="font-bold text-base text-white mb-1 truncate">{p.title || "Untitled Project"}</h3>
                    <p className="text-xs text-zinc-400 line-clamp-2 mb-4">
                      {p.scenes?.[0]?.narration || "Story project generated with AI director."}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-zinc-500 pt-3 border-t border-zinc-800/80">
                      <span>{p.created_at ? new Date(p.created_at).toLocaleDateString() : "Saved Project"}</span>
                      <span className="flex items-center text-amber-400 font-semibold hover:underline">
                        Open Studio <ChevronRight className="w-3 h-3 ml-0.5" />
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 3: SCENE & SHOT STORYBOARD EDITOR */}
        {activeTab === "storyboard" && plan && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white">{plan.title} – Cinematic Shot Board</h2>
                <p className="text-xs text-zinc-400">
                  {plan.scenes.length} Scenes divided into multi-shot sequences optimized for {targetModel}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                {plan.scenes.map((scene) => (
                  <div
                    key={scene.id}
                    onClick={() => setSelectedScene(scene)}
                    className={`bg-zinc-900/60 backdrop-blur-xl border rounded-2xl p-5 cursor-pointer transition-all ${
                      selectedScene?.id === scene.id ? "border-amber-500 bg-amber-500/5 shadow-lg shadow-amber-500/10" : "border-zinc-800 hover:border-zinc-700"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="w-6 h-6 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-bold flex items-center justify-center">
                          S{scene.order}
                        </span>
                        <h4 className="font-bold text-sm text-white">{scene.title}</h4>
                      </div>
                      <span className="text-xs text-zinc-400 font-mono">{scene.duration_seconds}s</span>
                    </div>

                    <p className="text-xs text-zinc-300 leading-relaxed mb-3 bg-zinc-950/60 p-3 rounded-xl border border-zinc-800/80">
                      &quot;{scene.narration}&quot;
                    </p>

                    {/* Scene Video Player Preview */}
                    <div className="my-3 overflow-hidden rounded-xl border border-zinc-800 bg-black">
                      <video
                        key={`${plan.id}-${scene.order}`}
                        controls
                        preload="metadata"
                        className="w-full aspect-video object-cover"
                      >
                        <source
                          src={`${API_BASE_URL}/exports/${plan.id}/videos/scene_${String(scene.order).padStart(3, "0")}.mp4`}
                          type="video/mp4"
                        />
                        Your browser does not support HTML5 video playback.
                      </video>
                    </div>

                    {/* Shots Breakdown */}
                    {scene.shots && scene.shots.length > 0 && (
                      <div className="space-y-2 mt-3 pt-3 border-t border-zinc-800/80">
                        <span className="text-[10px] font-semibold text-amber-400 uppercase tracking-wider">Multi-Shot Breakdown ({scene.shots.length} Shots)</span>
                        <div className="grid grid-cols-3 gap-2">
                          {scene.shots.map((shot) => (
                            <div key={shot.id} className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800 text-[11px]">
                              <span className="font-bold text-white block capitalize">{shot.shot_type.replace("_", " ")}</span>
                              <span className="text-zinc-400 text-[10px] block truncate">{shot.camera_movement}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Scene Inspector Sidebar */}
              <div>
                {selectedScene ? (
                  <div className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-5 sticky top-24 space-y-4">
                    <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                      <h3 className="font-bold text-sm text-white">Scene #{selectedScene.order} Inspector</h3>
                      <button onClick={() => setSelectedScene(null)} className="text-zinc-500 hover:text-white">
                        <X className="w-4 h-4" />
                      </button>
                    </div>

                    <div>
                      <span className="text-[10px] font-semibold text-zinc-400 uppercase">Target Video Prompt</span>
                      <div className="bg-zinc-950 p-3 rounded-xl border border-zinc-800 mt-1 text-xs text-zinc-300 leading-relaxed relative group">
                        {selectedScene.prompt}
                        <button
                          onClick={() => copyToClipboard(selectedScene.prompt, "prompt")}
                          className="absolute top-2 right-2 p-1.5 bg-zinc-800 hover:bg-zinc-700 rounded-md text-zinc-300 opacity-0 group-hover:opacity-100 transition"
                        >
                          {copiedText === "prompt" ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>

                    <div>
                      <span className="text-[10px] font-semibold text-zinc-400 uppercase">Negative Prompt</span>
                      <div className="bg-zinc-950 p-3 rounded-xl border border-zinc-800 mt-1 text-xs text-zinc-400">
                        {selectedScene.negative_prompt}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-8 text-center text-zinc-500">
                    <Camera className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-xs">Click any scene to inspect detailed prompts and shots.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: CHARACTER LIBRARY */}
        {activeTab === "characters" && plan && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Permanent Character Library</h2>
              <p className="text-xs text-zinc-400">Master character visual profiles maintained across all generated prompts</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {plan.characters?.map((c) => (
                <div key={c.id} className="bg-zinc-900/60 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6 space-y-4 shadow-xl">
                  <div className="flex items-center space-x-3 border-b border-zinc-800 pb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-amber-500 to-purple-600 p-0.5">
                      <div className="w-full h-full bg-zinc-950 rounded-full flex items-center justify-center font-bold text-amber-400 text-sm">
                        {c.name.charAt(0)}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-bold text-base text-white">{c.name}</h3>
                      <p className="text-xs text-zinc-400">{c.age || "Unknown age"} • {c.gender || "Unknown"}</p>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-zinc-300">
                    <p><span className="text-zinc-500 font-semibold">Height / Build:</span> {c.height || c.body_type || "N/A"}</p>
                    <p><span className="text-zinc-500 font-semibold">Face / Hair:</span> {c.face || c.face_shape || "Standard"} • {c.hair || c.hairstyle || "Standard"}</p>
                    <p><span className="text-zinc-500 font-semibold">Eyes / Skin:</span> {c.eyes || c.eye_colour || "Dark"} • {c.skin_tone || "Olive"}</p>
                    <p><span className="text-zinc-500 font-semibold">Attire:</span> {c.clothing || "Story Attire"}</p>
                    <p><span className="text-zinc-500 font-semibold">Power Level:</span> <span className="text-amber-400 font-bold">{c.power_level || "Normal"}</span></p>
                    {c.abilities && c.abilities.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {c.abilities.map((a, i) => (
                          <span key={i} className="px-2 py-0.5 bg-zinc-800 text-zinc-300 text-[10px] rounded-md border border-zinc-700">
                            {a}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: LOCATION LIBRARY */}
        {activeTab === "locations" && plan && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Environment & Location Library</h2>
              <p className="text-xs text-zinc-400">Reusable environmental profiles ensuring lighting and architectural continuity</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {plan.locations?.map((l) => (
                <div key={l.id} className="bg-zinc-900/60 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6 space-y-4 shadow-xl">
                  <div className="flex items-center space-x-3 border-b border-zinc-800 pb-3">
                    <div className="p-2 bg-amber-500/10 rounded-xl border border-amber-500/20 text-amber-400">
                      <MapPin className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-base text-white">{l.name}</h3>
                      <p className="text-xs text-zinc-400">{l.time_of_day || "Dusk"} • {l.weather || "Clear"}</p>
                    </div>
                  </div>

                  <div className="space-y-2 text-xs text-zinc-300">
                    <p><span className="text-zinc-500 font-semibold">Architecture:</span> {l.architecture || "N/A"}</p>
                    <p><span className="text-zinc-500 font-semibold">Lighting:</span> {l.lighting || "Atmospheric"}</p>
                    <p><span className="text-zinc-500 font-semibold">Textures:</span> {l.textures || "Standard"}</p>
                    <p><span className="text-zinc-500 font-semibold">Palette:</span> {l.colour_palette || "Cinematic"}</p>
                    {l.props && l.props.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {l.props.map((p, i) => (
                          <span key={i} className="px-2 py-0.5 bg-zinc-800 text-zinc-300 text-[10px] rounded-md border border-zinc-700">
                            {p}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 6: AUDIO & SSML STUDIO */}
        {activeTab === "audio_studio" && plan && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Audio & SSML Sound Studio</h2>
              <p className="text-xs text-zinc-400">Voice scripts, sound effect cue sheets, and background music parameters</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* SSML Voice Inspector */}
              <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 space-y-4">
                <div className="flex items-center space-x-2 border-b border-zinc-800 pb-3">
                  <Volume2 className="w-5 h-5 text-amber-400" />
                  <h3 className="font-bold text-sm text-white">SSML Voice Script Inspector</h3>
                </div>

                <div className="space-y-3">
                  {plan.voice_script?.map((v, i) => (
                    <div key={i} className="bg-zinc-950 p-4 rounded-xl border border-zinc-800 space-y-2">
                      <div className="flex items-center justify-between text-xs font-semibold text-amber-400">
                        <span>Speaker: {v.speaker} (Scene #{v.scene_order})</span>
                        <span className="text-zinc-500 font-normal">Emotion: {v.voice_emotion}</span>
                      </div>
                      <p className="text-xs text-zinc-300">{v.text}</p>
                      <pre className="text-[10px] font-mono text-emerald-400 bg-zinc-900/80 p-2 rounded border border-zinc-800 overflow-x-auto">
                        {v.ssml_text}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>

              {/* SFX & Music Cues */}
              <div className="space-y-6">
                <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center space-x-2 border-b border-zinc-800 pb-3">
                    <Zap className="w-5 h-5 text-amber-400" />
                    <h3 className="font-bold text-sm text-white">Sound Effects Cue Sheet (SFX)</h3>
                  </div>
                  <div className="space-y-2">
                    {plan.sfx_plan?.map((sfx, i) => (
                      <div key={i} className="flex items-center justify-between bg-zinc-950 p-3 rounded-xl border border-zinc-800 text-xs">
                        <div>
                          <span className="font-bold text-white capitalize">{sfx.category}: </span>
                          <span className="text-zinc-400">{sfx.description}</span>
                        </div>
                        <span className="text-[10px] font-mono text-amber-400 bg-zinc-900 px-2 py-1 rounded">
                          @{sfx.timing_seconds}s
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 space-y-4">
                  <div className="flex items-center space-x-2 border-b border-zinc-800 pb-3">
                    <Music className="w-5 h-5 text-purple-400" />
                    <h3 className="font-bold text-sm text-white">Background Music Track Parameters</h3>
                  </div>
                  <div className="space-y-2">
                    {plan.music_plan?.map((m, i) => (
                      <div key={i} className="bg-zinc-950 p-3 rounded-xl border border-zinc-800 text-xs space-y-1">
                        <div className="flex items-center justify-between font-bold text-white">
                          <span>{m.genre} ({m.mood})</span>
                          <span className="text-purple-400">{m.tempo}</span>
                        </div>
                        <p className="text-[11px] text-zinc-400">Intensity: {m.intensity}/10 • Transition: {m.transition_point}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 7: RENDER QUEUE & VIDEO PLAYER */}
        {activeTab === "render_queue" && plan && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Rendering Queue & Movie Player</h2>
              <p className="text-xs text-zinc-400">Real-time status tracking for video generation & final movie assembly</p>
            </div>

            {/* Progress Bar */}
            <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-6 space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="font-semibold text-white">Movie Rendering Progress</span>
                <span className="font-mono text-amber-400 font-bold">{progressPercent}%</span>
              </div>
              <div className="w-full bg-zinc-950 h-3 rounded-full overflow-hidden p-0.5 border border-zinc-800">
                <div
                  className="bg-gradient-to-r from-amber-500 to-orange-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>

            {movieExport?.warnings && movieExport.warnings.length > 0 && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-5 text-sm text-red-200">
                <p className="font-semibold text-red-300">Render needs attention</p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-xs leading-relaxed text-red-200/90">
                  {movieExport.warnings.map((warning, index) => (
                    <li key={`${warning}-${index}`}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Final Stitched Movie Player */}
            <div className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-sm text-white flex items-center space-x-2">
                  <Film className="w-4 h-4 text-emerald-400" />
                  <span>Stitched Final Movie Asset</span>
                </h3>
                <a
                  href={`${API_BASE_URL}/exports/${plan.id}/final_movie.mp4`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-amber-400 hover:underline flex items-center space-x-1"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Direct Download MP4</span>
                </a>
              </div>
              <video
                key={plan.id}
                controls
                preload="metadata"
                className="w-full rounded-xl border border-zinc-800 aspect-video bg-black shadow-2xl"
              >
                <source src={`${API_BASE_URL}/exports/${plan.id}/final_movie.mp4`} type="video/mp4" />
                Your browser does not support video playback.
              </video>
            </div>
          </div>
        )}

        {/* TAB 8: EXPORT HUB */}
        {activeTab === "export_hub" && plan && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Production Asset Export Hub</h2>
              <p className="text-xs text-zinc-400">Download complete movie studio packages, bibles, and scripts</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { title: "HTML Storyboard", desc: "Printable visual scene board", file: "storyboard.html" },
                { title: "Character Bible", desc: "Full Markdown character sheets", file: "character_bible.md" },
                { title: "Location Bible", desc: "Full Markdown location sheets", file: "location_bible.md" },
                { title: "Prompt Pack", desc: "JSON prompt history", file: "prompt_history.json" },
                { title: "Voice SSML", desc: "SSML narration & dialogue script", file: "voice_script.ssml" },
                { title: "Sound Effects", desc: "SFX cue beat sheet", file: "sfx_plan.json" },
                { title: "Subtitles (SRT)", desc: "Time-aligned subtitles", file: "subtitles.srt" },
                { title: "Final Movie MP4", desc: "Stitched full video", file: "final_movie.mp4" },
              ].map((item, idx) => (
                <a
                  key={idx}
                  href={`${API_BASE_URL}/exports/${plan.id}/${item.file}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-5 hover:border-amber-500/50 hover:bg-zinc-800/40 transition group"
                >
                  <Download className="w-6 h-6 text-amber-400 mb-2 group-hover:scale-110 transition-transform" />
                  <h4 className="font-bold text-sm text-white">{item.title}</h4>
                  <p className="text-xs text-zinc-400 mt-1">{item.desc}</p>
                </a>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
