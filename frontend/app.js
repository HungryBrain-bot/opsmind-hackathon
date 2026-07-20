const API = "/api/v1";
const scenarios = {
  certificate_expiry: {caseId:"INC-2026-0719-001",title:"Heavy Forwarder stopped forwarding production logs",summary:"Production monitoring detected a sustained ingestion outage from HF-PROD-02 after repeated TLS failures."},
  firewall_block: {caseId:"INC-2026-0718-014",title:"No events reaching the indexer cluster",summary:"A forwarding path is unavailable even though the source service remains healthy."},
  outputs_misconfiguration: {caseId:"INC-2026-0716-003",title:"Forwarding failure after maintenance",summary:"Production ingestion stopped shortly after a configuration maintenance window."},
  disk_full: {caseId:"INC-2026-0714-027",title:"Ingestion delay and growing queues",summary:"Heavy Forwarder queues are increasing while event delivery falls behind."}
};
let currentId=null, workspace=null, pollTimer=null, playbackTimers=[], executive=false;
const $=id=>document.getElementById(id);
const pct=value=>`${Math.round((value||0)*100)}%`;
const escapeHtml=value=>String(value??"").replace(/[&<>'"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));

function toast(message){const el=$("toast");el.textContent=message;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2400)}
function setScenario(){const data=scenarios[$("scenarioSelect").value];$("caseId").textContent=data.caseId;$("incidentTitle").textContent=data.title;$("incidentSummary").textContent=data.summary}
function setBusy(busy){$("runButton").disabled=busy;$("scenarioSelect").disabled=busy;$("runButton").textContent=busy?"Investigating…":"Start golden investigation"}

async function startInvestigation(){
  stopPlayback(); setBusy(true); currentId=null; workspace=null; resetWorkspace();
  const data=scenarios[$("scenarioSelect").value];
  try{
    const response=await fetch(`${API}/investigations`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({problem:data.title,environment:"Production",priority:"High",scenario_id:$("scenarioSelect").value})});
    if(!response.ok) throw new Error(`API returned ${response.status}`);
    const result=await response.json(); currentId=result.investigation_id; toast(`Investigation ${currentId} started`); await refreshWorkspace();
    pollTimer=setInterval(refreshWorkspace,650);
  }catch(error){setBusy(false);toast(`Unable to start: ${error.message}`)}
}

async function refreshWorkspace(){
  if(!currentId)return;
  try{
    const response=await fetch(`${API}/investigations/${currentId}/workspace`); if(!response.ok)throw new Error("Workspace unavailable");
    workspace=await response.json(); renderWorkspace(workspace);
    if(["completed","inconclusive","failed"].includes(workspace.status)){clearInterval(pollTimer);pollTimer=null;setBusy(false);$("playbackButton").disabled=!workspace.playback_events.length;toast(workspace.status==="completed"?"Investigation complete":"Investigation finished");}
  }catch(error){clearInterval(pollTimer);setBusy(false);toast(error.message)}
}

function resetWorkspace(){
  $("statusPill").className="pill running";$("statusPill").textContent="Investigating";$("phaseValue").textContent="Intake";$("roundValue").textContent="0";$("confidenceValue").textContent="0%";$("evidenceValue").textContent="0";$("completenessValue").textContent="0%";$("playbackButton").disabled=true;
}

function renderWorkspace(w){
  const complete=w.status==="completed";
  $("statusPill").className=`pill ${complete?"complete":"running"}`;$("statusPill").textContent=w.status.replaceAll("_"," ");
  $("phaseValue").textContent=w.phase.replaceAll("_"," ");$("roundValue").textContent=w.round_number;$("confidenceValue").textContent=pct(w.overall_confidence);$("evidenceValue").textContent=w.graph.nodes.filter(n=>n.node_type==="evidence").length;$("completenessValue").textContent=pct(w.completeness);
  $("leadingHypothesis").textContent=w.leading_hypothesis||"No leading hypothesis yet";$("verdictText").textContent=w.verdict||"OpsMind is collecting evidence and testing competing explanations.";$("verdictBadge").className=`pill ${complete?"complete":"warning"}`;$("verdictBadge").textContent=complete?"Defensible":"Investigating";
  $("scoreRingValue").textContent=pct(w.overall_confidence);$("scoreRing").style.setProperty("--score",`${Math.round(w.overall_confidence*360)}deg`);$("confidenceReason").textContent=w.timeline.at(-1)?.detail||"Evidence is being evaluated.";$("nextAction").textContent=w.next_action||"Investigation complete";
  updatePhases(w.phase,complete);renderConfidence(w);renderGraph(w.graph);renderHypotheses(w);renderTrust(w);renderTimeline(w.timeline);renderResolution(w);renderKnowledge(w.knowledge_capture);$("approvalBadge").className=`pill ${w.resolution.length?"warning":"neutral"}`;$("approvalBadge").textContent=w.resolution.length?"Human approval required":"Awaiting verdict";
}

function updatePhases(active,complete){const order=["intake","planning","evidence_collection","reasoning","resolution","verification","knowledge_capture"];const activeIndex=complete?order.length:Math.max(0,order.indexOf(active));document.querySelectorAll(".phase").forEach((el,index)=>{el.classList.toggle("active",index===activeIndex&&!complete);el.classList.toggle("done",index<activeIndex||complete)})}

function renderConfidence(w){
  const svg=$("confidenceChart"),points=w.confidence_evolution;$("roundBadge").textContent=`${points.length} round${points.length===1?"":"s"}`;
  let html='<defs><linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#31d0aa" stop-opacity=".28"/><stop offset="100%" stop-color="#31d0aa" stop-opacity="0"/></linearGradient></defs>';
  [20,60,100,140,180].forEach(y=>html+=`<line class="chart-grid" x1="42" y1="${y}" x2="615" y2="${y}"/>`);
  if(!points.length){html+='<text class="chart-label" x="250" y="120">Confidence history appears after evidence evaluation</text>';svg.innerHTML=html;$("confidenceLegend").innerHTML="<span>No evidence rounds completed.</span>";return}
  const coords=points.map((p,i)=>({x:points.length===1?320:60+i*(530/(points.length-1)),y:190-p.confidence*160,p}));const path=coords.map((c,i)=>`${i?"L":"M"}${c.x},${c.y}`).join(" ");const area=`${path} L${coords.at(-1).x},200 L${coords[0].x},200 Z`;html+=`<path class="chart-area" d="${area}"/><path class="chart-line" d="${path}"/>`;coords.forEach(c=>html+=`<circle class="chart-point" cx="${c.x}" cy="${c.y}" r="6"/><text class="chart-label" x="${c.x-18}" y="218">R${c.p.round_number}</text><text class="chart-label" x="${c.x-14}" y="${c.y-13}">${pct(c.p.confidence)}</text>`);svg.innerHTML=html;$("confidenceLegend").innerHTML=points.map(p=>`<span><strong>${escapeHtml(p.label)}</strong> · ${escapeHtml(p.reason)}</span>`).join("");
}

function graphLayout(nodes){
  const groups={incident:[],hypothesis:[],evidence:[],entity:[],resolution:[]};nodes.forEach(n=>(groups[n.node_type]||groups.entity).push(n));const positions={};
  const place=(items,y,start,end)=>items.forEach((n,i)=>{positions[n.id]={x:items.length===1?(start+end)/2:start+i*((end-start)/Math.max(1,items.length-1)),y}});
  place(groups.incident,70,500,500);place(groups.hypothesis,210,140,860);place(groups.evidence,385,90,910);place(groups.entity,530,120,720);place(groups.resolution,530,880,880);return positions;
}
function renderGraph(graph){
  const svg=$("evidenceGraph"),positions=graphLayout(graph.nodes);let html='<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#53657d"/></marker></defs>';
  graph.edges.forEach(e=>{const a=positions[e.source],b=positions[e.target];if(a&&b)html+=`<line class="edge ${e.edge_type}" x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" marker-end="url(#arrow)"/>`});
  graph.nodes.forEach(n=>{const p=positions[n.id],r=n.node_type==="incident"?48:n.node_type==="resolution"?42:n.node_type==="hypothesis"?38:30;const label=n.label.length>25?n.label.slice(0,25)+"…":n.label;html+=`<g class="graph-node ${n.node_type}" data-node="${escapeHtml(n.id)}" transform="translate(${p.x},${p.y})"><circle r="${r}"/><text y="-2">${escapeHtml(label)}</text>${n.confidence!=null?`<text class="node-sub" y="15">${pct(n.confidence)}</text>`:""}</g>`});svg.innerHTML=html;svg.querySelectorAll(".graph-node").forEach(el=>el.addEventListener("click",()=>inspectNode(graph.nodes.find(n=>n.id===el.dataset.node),el)));
}
function inspectNode(node,el){document.querySelectorAll(".graph-node").forEach(n=>n.classList.remove("selected"));el.classList.add("selected");$("nodeInspector").className="inspector-detail";$("nodeInspector").innerHTML=`<span class="pill neutral">${escapeHtml(node.node_type)}</span><h2>${escapeHtml(node.label)}</h2><p>${escapeHtml(node.detail||node.subtitle||"Enterprise relationship node")}</p><div class="inspector-meta"><div><span>Status</span><strong>${escapeHtml(node.status)}</strong></div>${node.confidence!=null?`<div><span>Confidence</span><strong>${pct(node.confidence)}</strong></div>`:""}${Object.entries(node.metadata||{}).map(([k,v])=>`<div><span>${escapeHtml(k.replaceAll("_"," "))}</span><strong>${escapeHtml(v)}</strong></div>`).join("")}</div>`}

function renderHypotheses(w){$("hypothesisCount").textContent=`${w.hypotheses.length} hypotheses`;$("hypothesisBoard").innerHTML=w.hypotheses.length?w.hypotheses.map((h,i)=>`<div class="hypothesis-card ${i===0?"leading":""}"><div class="hypothesis-head"><strong>${escapeHtml(h.title)}</strong><span>${pct(h.confidence)}</span></div><p>${escapeHtml(h.rationale)}</p><div class="bar"><i style="width:${h.confidence*100}%"></i></div><div class="evidence-chip-row">${h.supporting_evidence_ids.map(id=>`<span class="evidence-chip">+ ${escapeHtml(id)}</span>`).join("")}${h.contradicting_evidence_ids.map(id=>`<span class="evidence-chip negative">− ${escapeHtml(id)}</span>`).join("")}</div>${h.rejection_reason?`<p class="rejection">Rejected: ${escapeHtml(h.rejection_reason)}</p>`:""}</div>`).join(""):"<p class='empty'>Competing explanations will appear here.</p>"}
function renderTrust(w){const contradictions=w.hypotheses.flatMap(h=>h.contradicting_evidence_ids.map(id=>`${id} challenges ${h.title}`));$("contradictions").innerHTML=contradictions.length?contradictions.map(x=>`<div class="list-item">${escapeHtml(x)}</div>`).join(""):"<p class='empty'>No unresolved contradictions.</p>";$("missingEvidence").innerHTML=w.missing_evidence.length?w.missing_evidence.map(x=>`<div class="list-item gap">${escapeHtml(x)}</div>`).join(""):"<p class='empty'>No critical evidence gaps remain.</p>"}
function renderTimeline(items){$("timeline").innerHTML=items.length?items.map((item,i)=>`<div class="timeline-event active" data-index="${i}"><span>${escapeHtml(item.phase)}</span><strong>${escapeHtml(item.title)}</strong><p>${escapeHtml(item.detail)}</p></div>`).join(""):"<p class='empty'>The investigation's reasoning trail will appear here.</p>"}

function renderResolution(w){
  $("resolutionFlow").innerHTML=w.resolution.length?w.resolution.map((r,i)=>`<div class="resolution-step"><span class="stage-index">${i+1} · ${escapeHtml(r.stage)}</span><h4>${escapeHtml(r.action)}</h4><p>${escapeHtml(r.rationale)}</p><span class="risk">${escapeHtml(r.risk)} risk</span><div class="evidence-chip-row">${r.evidence_ids.map(id=>`<span class="evidence-chip">${escapeHtml(id)}</span>`).join("")}</div></div>`).join(""):"<p class='empty'>Containment, recovery, verification, rollback and prevention steps will appear after root cause is established.</p>";
  $("verificationList").innerHTML=w.verification.length?w.verification.map(v=>`<div class="verification-item"><span>${v.status==="passed"?"✓":"○"}</span><div><strong>${escapeHtml(v.metric)} ${escapeHtml(v.condition)} ${escapeHtml(v.expected_value)}</strong><small>${escapeHtml(v.source)}</small></div></div>`).join(""):"<p class='empty'>No verification plan yet.</p>";
}
function renderKnowledge(k){$("knowledgeCard").innerHTML=k?`<h4>${escapeHtml(k.title)}</h4><p><strong>Root cause:</strong> ${escapeHtml(k.root_cause)}</p><p>${(k.resolution_summary||[]).map(escapeHtml).join(" · ")}</p><div class="tag-row">${(k.tags||[]).map(t=>`<span>${escapeHtml(t)}</span>`).join("")}</div>`:"<p class='empty'>A reusable incident pattern will be captured after resolution.</p>"}

function stopPlayback(){playbackTimers.forEach(clearTimeout);playbackTimers=[];$("playbackProgress").style.width="0";$("playbackStatus").textContent="Waiting"}
function playInvestigation(){if(!workspace?.playback_events?.length)return;stopPlayback();const events=workspace.playback_events;document.querySelectorAll(".timeline-event").forEach(e=>e.classList.remove("active"));$("playbackStatus").textContent="Replaying";events.forEach((event,i)=>{playbackTimers.push(setTimeout(()=>{const item=document.querySelector(`.timeline-event[data-index="${i}"]`);item?.classList.add("active");item?.scrollIntoView({behavior:"smooth",block:"nearest",inline:"center"});$("playbackProgress").style.width=`${((i+1)/events.length)*100}%`;$("playbackStatus").textContent=event.title;if(i===events.length-1)setTimeout(()=>$("playbackStatus").textContent="Replay complete",500)},i*700))})}
function toggleView(){executive=!executive;document.body.classList.toggle("executive",executive);$("viewModeButton").textContent=executive?"Executive view":"Engineer view";toast(executive?"Executive summary enabled":"Engineer detail enabled")}

document.querySelectorAll(".nav-item").forEach(button=>button.addEventListener("click",()=>{document.querySelectorAll(".nav-item").forEach(b=>b.classList.remove("active"));button.classList.add("active");document.getElementById(button.dataset.scroll)?.scrollIntoView({behavior:"smooth"})}));
$("scenarioSelect").addEventListener("change",setScenario);$("runButton").addEventListener("click",startInvestigation);$("playbackButton").addEventListener("click",playInvestigation);$("viewModeButton").addEventListener("click",toggleView);setScenario();
