import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageSquare, 
  Code, 
  FileText, 
  Send, 
  PanelLeftClose, 
  PanelLeftOpen, 
  Trash2, 
  Plus, 
  X,
  Play,
  Timer,
  CheckCircle2,
  Maximize2,
  Minimize2,
  Dumbbell,
  History,
  Loader2,
  ChevronRight,
  Target
} from 'lucide-react';

const apiKey = ""; 
const MODEL_NAME = "gemini-2.5-flash-preview-09-2025";

const App = () => {
  // --- UI State ---
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isFullScreenChat, setIsFullScreenChat] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // --- Workout Logic State ---
  const [timeLeft, setTimeLeft] = useState(0);

  // --- Dynamic Panes State ---
  const [panes, setPanes] = useState([
    { id: 'log', title: 'Workout Log', content: '_No workout started._', type: 'text', color: 'blue' },
    { id: 'tracker', title: 'Active Set', content: 'Ready for assignment.', type: 'form', color: 'green' }
  ]);

  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: "Coach here. Give me a target (e.g., 'Leg Day') and I'll push the workout to your trackers." 
    }
  ]);

  const [userInput, setUserInput] = useState("");
  const scrollRef = useRef(null);

  // --- Timer Effect ---
  useEffect(() => {
    let interval;
    if (timeLeft > 0) {
      interval = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [timeLeft]);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  // --- AI Command Processing ---
  const processAIResponse = (text) => {
    let cleanText = text;
    
    const updateRegex = /\[UPDATE_PANE:(\w+)\]([\s\S]*?)\[\/UPDATE_PANE\]/g;
    let match;
    while ((match = updateRegex.exec(text)) !== null) {
      const [full, id, newContent] = match;
      setPanes(prev => prev.map(p => p.id === id ? { ...p, content: newContent.trim() } : p));
      cleanText = cleanText.replace(full, `*(Updated ${id})*`);
    }

    const addRegex = /\[ADD_PANE:(\w+):(.+?)\]([\s\S]*?)\[\/ADD_PANE\]/g;
    while ((match = addRegex.exec(text)) !== null) {
      const [full, type, title, content] = match;
      const newId = `pane_${Date.now()}`;
      setPanes(prev => [...prev, { id: newId, title, content: content.trim(), type, color: 'purple' }]);
      cleanText = cleanText.replace(full, `*(Added ${title})*`);
    }

    return cleanText;
  };

  const handleSendMessage = async (e, customPrompt = null) => {
    if (e) e.preventDefault();
    const messageToSend = customPrompt || userInput;
    if (!messageToSend.trim() || isLoading) return;

    if (!customPrompt) {
      setMessages(prev => [...prev, { role: 'user', content: messageToSend }]);
      setUserInput("");
    }
    
    setIsLoading(true);

    try {
      const systemInstruction = `You are an elite Strength Coach. 
      Current Panes: ${panes.map(p => `[ID: ${p.id}, Title: ${p.title}]`).join(', ')}
      
      COMMANDS:
      - [UPDATE_PANE:log]markdown content[/UPDATE_PANE]
      - [UPDATE_PANE:tracker]Exercise Name | Weight | Reps | RPE | RestSecs[/UPDATE_PANE]

      FORMAT FOR TRACKER PANE:
      Always use this pipe-delimited format for the tracker: 
      "Bench Press | 225 | 5 | 8 | 90"

      When the user finishes a set, acknowledge the performance and update the tracker for the NEXT set immediately.`;

      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: messageToSend }] }],
          systemInstruction: { parts: [{ text: systemInstruction }] }
        })
      });

      const data = await response.json();
      const rawText = data.candidates?.[0]?.content?.parts?.[0]?.text || "";

      setMessages(prev => [...prev, { role: 'assistant', content: processAIResponse(rawText) }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Connection lost. Focus on the lift." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSetComplete = (weight, reps, rpe, rest) => {
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const logEntry = `\n- **Set Complete**: ${weight}lbs x ${reps} @ RPE ${rpe} (${timestamp})`;
    const restNote = `\n  <small style="color: #6b7280; opacity: 0.6;">Rest: ${rest}s</small>`;
    
    setPanes(prev => prev.map(p => p.id === 'log' ? { ...p, content: p.content + logEntry + restNote } : p));
    setTimeLeft(parseInt(rest));
    
    handleSendMessage(null, `Finished set: ${weight}x${reps} @ RPE ${rpe}. Get me the next one.`);
  };

  return (
    <div className="flex h-screen w-full bg-black text-gray-200 font-sans overflow-hidden">
      
      {/* Sidebar / Chat */}
      <aside className={`transition-all duration-500 bg-gray-950 border-r border-gray-900 flex flex-col overflow-hidden ${isFullScreenChat ? 'w-full' : isSidebarOpen ? 'w-96' : 'w-0'}`}>
        <div className="p-4 border-b border-gray-900 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-red-600 rounded-lg shadow-lg shadow-red-900/20"><Dumbbell size={18} className="text-white" /></div>
            <h2 className="font-black tracking-tighter text-white uppercase italic text-xl">Iron Coach</h2>
          </div>
          <div className="flex gap-1">
            <button onClick={() => setIsFullScreenChat(!isFullScreenChat)} className="p-2 hover:bg-gray-800 rounded text-gray-400">
              {isFullScreenChat ? <Minimize2 size={16}/> : <Maximize2 size={16}/>}
            </button>
          </div>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-red-600 text-white rounded-tr-none' : 'bg-gray-900 border border-gray-800 rounded-tl-none shadow-xl'}`}>
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}
          {isLoading && <div className="flex items-center gap-2 text-[10px] text-red-500 font-black animate-pulse uppercase tracking-widest"><Loader2 size={12} className="animate-spin" /> ANALYZING BIOMECHANICS...</div>}
        </div>

        <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-900 bg-gray-950">
          <div className="relative">
            <input 
              value={userInput} 
              onChange={e => setUserInput(e.target.value)}
              placeholder="Talk to coach..."
              className="w-full bg-gray-900 border border-gray-800 rounded-xl py-3 pl-4 pr-10 text-sm focus:ring-1 focus:ring-red-600 outline-none transition-all"
            />
            <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500 hover:text-red-400"><Send size={18}/></button>
          </div>
        </form>
      </aside>

      {/* Main Workspace */}
      {!isFullScreenChat && (
        <main className="flex-1 flex flex-col min-w-0 bg-black">
          <nav className="h-16 border-b border-gray-900 flex items-center justify-between px-6 bg-gray-950/80 backdrop-blur-md">
            <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 transition-colors">
              {isSidebarOpen ? <PanelLeftClose size={20}/> : <PanelLeftOpen size={20}/>}
            </button>
            
            {timeLeft > 0 ? (
              <div className="flex items-center gap-4 px-6 py-2 bg-red-600/10 border border-red-500/30 rounded-full animate-pulse">
                <Timer size={20} className="text-red-500" />
                <span className="text-lg font-black font-mono text-red-500 tracking-wider uppercase">RESTING: {timeLeft}s</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 px-4 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-ping"></div>
                <span className="text-xs font-bold text-green-500 uppercase tracking-widest">Active Session</span>
              </div>
            )}
            <div className="w-10"></div>
          </nav>

          <div className="flex-1 flex flex-col lg:flex-row overflow-hidden p-6 gap-6">
            {panes.map((pane) => (
              <div key={pane.id} className={`flex-1 flex flex-col border rounded-3xl overflow-hidden shadow-2xl transition-all ${pane.id === 'tracker' ? 'border-green-500/20 bg-green-500/[0.02]' : 'border-gray-800 bg-gray-900/10'}`}>
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800/50 bg-black/40">
                  <div className="flex items-center gap-2">
                    {pane.id === 'log' ? <History size={16} className="text-blue-400"/> : <Target size={16} className="text-green-400"/>}
                    <span className="text-xs font-black uppercase tracking-[0.2em] text-gray-500">{pane.title}</span>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                  {pane.type === 'form' ? (
                    <WorkoutForm onSubmit={handleSetComplete} dataString={pane.content} />
                  ) : (
                    <div className="text-sm prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: formatMarkdown(pane.content) }} />
                  )}
                </div>
              </div>
            ))}
          </div>
        </main>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .custom-scrollbar::-webkit-scrollbar { width: 4px; height: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 10px; }
        input[type=range]::-webkit-slider-thumb { border: 2px solid #22c55e; background: #000; height: 16px; width: 16px; border-radius: 50%; cursor: pointer; -webkit-appearance: none; margin-top: -6px; }
        input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 4px; cursor: pointer; background: #374151; border-radius: 2px; }
      `}} />
    </div>
  );
};

const WorkoutForm = ({ onSubmit, dataString }) => {
  // Parsing the coach string: "Exercise | Weight | Reps | RPE | Rest"
  const [exercise, rawWeight, rawReps, rawRpe, rawRest] = dataString.split('|').map(s => s.trim());
  
  const [weight, setWeight] = useState("");
  const [reps, setReps] = useState("");
  const [rpe, setRpe] = useState("7.0");
  const [rest, setRest] = useState("90");

  // Automatically fill when the instruction updates
  useEffect(() => {
    if (rawWeight) setWeight(rawWeight);
    if (rawReps) setReps(rawReps);
    if (rawRpe) setRpe(rawRpe);
    if (rawRest) setRest(rawRest);
  }, [dataString]);

  return (
    <div className="space-y-8">
      <div className="text-center mb-10">
        <span className="text-[10px] font-black uppercase tracking-[0.3em] text-green-500/60 mb-2 block">Current Objective</span>
        <h2 className="text-5xl font-black italic uppercase tracking-tighter text-white drop-shadow-lg leading-tight">
          {exercise || "Awaiting Exercise"}
        </h2>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white/5 p-4 rounded-2xl border border-white/10 shadow-inner">
          <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 block">Target Weight</label>
          <div className="flex items-baseline gap-2">
            <input 
              type="number" 
              value={weight} 
              onChange={e => setWeight(e.target.value)} 
              className="w-full bg-transparent text-4xl font-black text-white outline-none" 
            />
            <span className="text-gray-600 font-bold uppercase text-xs">lbs</span>
          </div>
        </div>
        <div className="bg-white/5 p-4 rounded-2xl border border-white/10 shadow-inner">
          <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2 block">Target Reps</label>
          <div className="flex items-baseline gap-2">
            <input 
              type="number" 
              value={reps} 
              onChange={e => setReps(e.target.value)} 
              className="w-full bg-transparent text-4xl font-black text-white outline-none" 
            />
            <span className="text-gray-600 font-bold uppercase text-xs">Reps</span>
          </div>
        </div>
      </div>

      <div className="bg-white/5 p-6 rounded-2xl border border-white/10">
        <label className="text-[10px] font-black text-gray-500 uppercase tracking-widest flex justify-between mb-4">
          Intensity (RPE) <span className="text-green-500 font-black text-sm">{rpe}</span>
        </label>
        <input 
          type="range" 
          min="1" max="10" step="0.5" 
          value={rpe} 
          onChange={e => setRpe(e.target.value)} 
          className="w-full bg-gray-800 h-1 rounded-lg appearance-none cursor-pointer" 
        />
        <div className="flex justify-between mt-2 text-[8px] font-bold text-gray-600 uppercase tracking-tighter">
          <span>Warmup</span>
          <span>Moderate</span>
          <span>Hard</span>
          <span>Max</span>
        </div>
      </div>

      <button 
        onClick={() => { if(weight && reps) onSubmit(weight, reps, rpe, rest); }}
        className="w-full py-6 bg-green-600 hover:bg-green-500 text-white rounded-2xl font-black uppercase tracking-[0.2em] text-lg shadow-xl shadow-green-900/20 active:scale-[0.98] transition-all flex items-center justify-center gap-3"
      >
        <CheckCircle2 size={24} />
        Log Set & Start Rest
      </button>

      <div className="pt-4 border-t border-gray-800/50 flex justify-center">
         <span className="text-[10px] text-gray-500 font-medium">Coach recommends {rest}s rest between sets</span>
      </div>
    </div>
  );
};

const formatMarkdown = (text) => {
  return text
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-black text-white mb-4 italic uppercase tracking-tighter border-b border-red-900/30 pb-2">$1</h1>')
    .replace(/^## (.*$)/gim, '<h2 class="text-lg font-bold text-red-500 mt-6 mb-2 uppercase tracking-widest">$1</h2>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
    .replace(/^- (.*$)/gim, '<li class="ml-2 mb-3 text-gray-300 flex items-start gap-3"><span class="text-red-500 mt-1">▹</span> <span>$1</span></li>')
    .replace(/<small style="(.*?)">(.*?)<\/small>/g, '<div class="text-[10px] opacity-40 italic ml-6 mb-4">$2</div>')
    .replace(/\n/g, '<br />');
};

export default App;