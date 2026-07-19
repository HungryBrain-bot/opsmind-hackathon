async function loadRuntime(){
  const badge=document.getElementById('modeBadge');
  try{
    const response=await fetch('/api/v1/runtime');
    if(!response.ok)throw new Error(`HTTP ${response.status}`);
    const runtime=await response.json();
    const isAI=runtime.mode==='openai';
    badge.textContent=isAI?`OpenAI · ${runtime.model}`:`Offline · Fixture`;
    badge.className=`mode-badge ${isAI?'openai':'offline'}`;
    badge.title=isAI?'Model-driven planning enabled':'Deterministic, reproducible planning enabled';
  }catch(error){
    badge.textContent='Mode unavailable';
    badge.className='mode-badge loading';
  }
}

loadRuntime();

const runButton=document.getElementById('runButton');
const downloadReportButton=document.getElementById('downloadReportButton');
const copyReportButton=document.getElementById('copyReportButton');
let eventSource=null;
let lastSnapshot=null;

function pct(v){return `${Math.round((v||0)*100)}%`;}
function escapeHtml(value=''){return String(value).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}


function enableReportActions(data){
  const terminal=['completed','inconclusive'].includes(data.status);
  downloadReportButton.disabled=!terminal;
  copyReportButton.disabled=!terminal;
}
function buildClipboardSummary(data){
  const leader=[...data.hypotheses].sort((a,b)=>b.confidence-a.confidence)[0];
  return [
    'OpsMind Investigation Summary',
    `Investigation: ${data.investigation_id}`,
    `Problem: ${data.problem}`,
    `Verdict: ${data.verdict||'No verdict generated'}`,
    `Leading confidence: ${leader?pct(leader.confidence):'N/A'}`,
    '',
    'Evidence:',
    ...data.evidence.map(e=>`- ${e.id}: ${e.title} (${e.source})`),
    '',
    'Recommended actions:',
    ...(data.recommended_actions||[]).map((a,i)=>`${i+1}. ${a}`)
  ].join('\n');
}
downloadReportButton.addEventListener('click',()=>{
  if(lastSnapshot)window.location.href=`/api/v1/investigations/${lastSnapshot.investigation_id}/report.md`;
});
copyReportButton.addEventListener('click',async()=>{
  if(!lastSnapshot)return;
  await navigator.clipboard.writeText(buildClipboardSummary(lastSnapshot));
  copyReportButton.textContent='Copied';
  setTimeout(()=>copyReportButton.textContent='Copy summary',1200);
});

function updateSteps(data){
  const phaseIndex=data.progress_percent>=100?4:data.progress_percent>=85?3:data.progress_percent>=35?2:data.progress_percent>=15?1:0;
  [...document.querySelectorAll('.step')].forEach((step,index)=>{
    step.classList.toggle('done',index<phaseIndex||data.progress_percent===100);
    step.classList.toggle('active',index===phaseIndex&&data.progress_percent<100);
  });
}

function renderRules(data){
  const rules=[
    ...data.stop_reason.rules_passed.map(x=>({name:x,state:'pass'})),
    ...data.stop_reason.rules_failed.map(x=>({name:x,state:'fail'})),
  ];
  document.getElementById('sufficiencyBadge').textContent=data.stop_reason.sufficient?'Sufficient':'Evidence pending';
  document.getElementById('sufficiencyBadge').className=data.stop_reason.sufficient?'badge success':'badge neutral';
  document.getElementById('rules').innerHTML=rules.length?rules.map(r=>
    `<div class="rule ${r.state}"><strong>${r.state==='pass'?'✓ Passed':'× Pending'}</strong><span>${escapeHtml(r.name)}</span></div>`
  ).join(''):`<p class="empty">${escapeHtml(data.stop_reason.summary)}</p>`;
}

function renderPlan(data){
  document.getElementById('toolCount').textContent=`${data.tools_used.length} tools`;
  const requirements=data.planned_evidence||[];
  document.getElementById('plan').innerHTML=requirements.length?requirements.map(r=>{
    const used=data.tools_used.includes(r.preferred_tool);
    return `<div class="plan-row"><strong>${used?'✓':'○'} ${escapeHtml(r.description)}</strong><span>${escapeHtml(r.preferred_tool)}</span></div>`;
  }).join(''):'<p class="empty">Generating a bounded evidence plan…</p>';
}


function renderDecisionTrace(data){
  const container=document.getElementById('decisionTrace');
  const badge=document.getElementById('decisionTraceBadge');
  if(!data.hypotheses.length){
    container.innerHTML='<p class="empty">Decision explanations will appear as evidence is evaluated.</p>';
    badge.textContent='Waiting';
    return;
  }
  const leader=[...data.hypotheses].sort((a,b)=>b.confidence-a.confidence)[0];
  badge.textContent=data.stop_reason.sufficient?'Defensible':'Still evaluating';
  badge.className=data.stop_reason.sufficient?'badge success':'badge neutral';

  container.innerHTML=[...data.hypotheses]
    .sort((a,b)=>b.confidence-a.confidence)
    .map(h=>{
      const selected=h.id===leader.id;
      const support=h.supporting_evidence_ids||[];
      const contradict=h.contradicting_evidence_ids||[];
      let explanation='';
      if(selected){
        explanation=support.length
          ? `${h.title} is leading because ${support.length} evidence item(s) support it and it has the highest confidence.`
          : `${h.title} currently leads, but more direct evidence is still required.`;
      }else if(h.rejection_reason){
        explanation=h.rejection_reason;
      }else if(contradict.length){
        explanation=`Not selected because ${contradict.length} evidence item(s) contradict this explanation.`;
      }else if(!support.length){
        explanation=`Not selected because no collected evidence directly supports it.`;
      }else{
        explanation=`Not selected because its evidence-backed confidence remains below ${leader.title}.`;
      }
      return `<div class="decision-row ${selected?'selected':''}">
        <div class="decision-rank">${selected?'✓':'×'}</div>
        <div>
          <div class="decision-head">
            <strong>${escapeHtml(h.title)}</strong>
            <span>${pct(h.confidence)}</span>
          </div>
          <p>${escapeHtml(explanation)}</p>
          <div class="decision-evidence">
            ${support.map(id=>`<span class="supports">Supports · ${escapeHtml(id)}</span>`).join('')}
            ${contradict.map(id=>`<span class="contradicts">Contradicts · ${escapeHtml(id)}</span>`).join('')}
          </div>
        </div>
      </div>`;
    }).join('');
}

function renderGraph(data){
  const canvas=document.getElementById('graphCanvas');
  if(!data||!data.hypotheses.length){
    canvas.innerHTML='<p class="empty">Run an investigation to build the evidence graph.</p>';return;
  }
  const hypotheses=data.hypotheses.map((h,index)=>
    `<div class="graph-node hypothesis" style="grid-column:${1+index*3}/${4+index*3}">
      <strong>${escapeHtml(h.title)}</strong><small>${pct(h.confidence)} · ${h.status}</small>
    </div>`).join('');
  const evidence=data.evidence.slice(0,6).map((e,index)=>
    `<div class="graph-node evidence" style="grid-column:${1+index*2}/${3+index*2}">
      <strong>${escapeHtml(e.id)}</strong><small>${escapeHtml(e.title)}</small>
    </div>`).join('');
  const verdict=data.verdict?`<div class="graph-node verdict"><strong>Verdict</strong><small>${escapeHtml(data.verdict)}</small></div>`:'';
  canvas.innerHTML=`<div class="graph-node problem"><strong>Incident</strong><small>${escapeHtml(data.problem)}</small></div>${hypotheses}${evidence}${verdict}`;
}

function render(data){
  lastSnapshot=data;
  document.getElementById('investigationId').textContent=data.investigation_id;
  document.getElementById('currentPhase').textContent=data.current_phase;
  document.getElementById('progressText').textContent=`${data.progress_percent}%`;
  document.getElementById('progressBar').style.width=`${data.progress_percent}%`;
  document.getElementById('roundCount').textContent=data.round_number;
  document.getElementById('remainingCount').textContent=data.hypotheses.filter(h=>h.status!=='rejected').length;
  document.getElementById('evidenceCount').textContent=data.evidence.length;
  document.getElementById('nextAction').textContent=data.next_action||'No further automated action';
  document.getElementById('verdict').textContent=data.verdict||data.stop_reason.summary;

  const leading=[...data.hypotheses].sort((a,b)=>b.confidence-a.confidence)[0];
  document.getElementById('leadingHypothesis').textContent=leading?`Leader · ${pct(leading.confidence)}`:'No leader';

  const terminal=['completed','inconclusive','failed'].includes(data.status);
  const badge=document.getElementById('reviewBadge');
  badge.textContent=terminal?(data.human_review_required?'Human review required':'Complete'):'Investigating';
  badge.className=terminal?'badge success':'badge neutral';

  const strength=pct(data.evidence_strength),complete=pct(data.investigation_completeness);
  document.getElementById('strengthValue').textContent=strength;
  document.getElementById('completeValue').textContent=complete;
  document.getElementById('strengthLabel').textContent=data.evidence.length?`${data.evidence.length} evidence objects`:'Collecting evidence';
  document.getElementById('completeLabel').textContent=data.stop_reason.summary;
  document.getElementById('strengthRing').style.background=`conic-gradient(var(--green) ${strength},#27364d 0)`;
  document.getElementById('completeRing').style.background=`conic-gradient(var(--purple2) ${complete},#27364d 0)`;

  document.getElementById('actions').innerHTML=data.recommended_actions.map(x=>`<div>→ ${escapeHtml(x)}</div>`).join('');
  document.getElementById('hypotheses').innerHTML=data.hypotheses.length?data.hypotheses.map(h=>{
    const history=(h.confidence_history||[]);
    const latest=history[history.length-1];
    const historyRows=history.map(change=>`
      <div class="confidence-event ${change.direction}">
        <div class="confidence-dot"></div>
        <div>
          <div class="confidence-event-head">
            <strong>${pct(change.previous_confidence)} → ${pct(change.new_confidence)}</strong>
            <span>${escapeHtml(change.direction)}</span>
          </div>
          <p>${escapeHtml(change.reason)}</p>
          ${change.evidence_ids.length?`<div class="evidence-tags">${change.evidence_ids.map(id=>`<span>${escapeHtml(id)}</span>`).join('')}</div>`:''}
        </div>
      </div>`).join('');
    return `<div class="item hypothesis-item new-item">
      <button class="hypothesis-toggle" type="button" onclick="this.closest('.hypothesis-item').classList.toggle('expanded')">
        <div class="item-head"><strong>${escapeHtml(h.title)}</strong><span class="state ${h.status}">${h.status}</span></div>
        <p>${escapeHtml(h.rationale)}</p>
        <div class="confidence-summary"><strong>${pct(h.confidence)}</strong><span>${latest?escapeHtml(latest.direction):'initial'}</span></div>
        <div class="confidence-track"><div style="width:${pct(h.confidence)}"></div></div>
        <div class="evidence-tags">${h.supporting_evidence_ids.map(x=>`<span>+ ${escapeHtml(x)}</span>`).join('')}${h.contradicting_evidence_ids.map(x=>`<span>− ${escapeHtml(x)}</span>`).join('')}</div>
        ${h.rejection_reason?`<div class="rejection-reason">${escapeHtml(h.rejection_reason)}</div>`:''}
        <span class="expand-label">Confidence history ▾</span>
      </button>
      <div class="confidence-history">
        <h4>Confidence evolution</h4>
        ${historyRows||'<p class="empty">No confidence updates yet.</p>'}
      </div>
    </div>`;
  }).join(''):'<p class="empty">Generating competing hypotheses…</p>';
  document.getElementById('evidence').innerHTML=data.evidence.length?data.evidence.map(e=>
    `<div class="item new-item">
      <div class="item-head"><strong>${escapeHtml(e.title)}</strong><span class="state supported">${e.id}</span></div>
      <p>${escapeHtml(e.content)}<br><b>${escapeHtml(e.source)}</b> · ${escapeHtml(e.category)} · ${escapeHtml(e.reliability)}</p>
      <div class="evidence-tags">${e.entities.map(x=>`<span>${escapeHtml(x)}</span>`).join('')}</div>
    </div>`).join(''):'<p class="empty">Waiting for evidence collection…</p>';
  document.getElementById('timeline').innerHTML=data.timeline.length?data.timeline.map(e=>{
    const t=new Date(e.timestamp).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'});
    return `<div class="note new-item"><time>${t}</time><div><strong>${escapeHtml(e.title)}</strong><p>${escapeHtml(e.detail)}</p></div></div>`;
  }).join(''):'<p class="empty">Investigation notes will appear here.</p>';
  document.getElementById('timeline').scrollTop=document.getElementById('timeline').scrollHeight;

  enableReportActions(data);
  renderDecisionTrace(data);
  renderRules(data);
  renderPlan(data);
  renderGraph(data);
  updateSteps(data);
  document.querySelector('.progress-card').classList.toggle('event-live',!terminal);

  if(terminal){
    runButton.disabled=false;
    runButton.textContent='Run again';
    if(eventSource){eventSource.close();eventSource=null;}
  }
}

function connectEvents(id){
  if(eventSource)eventSource.close();
  eventSource=new EventSource(`/api/v1/investigations/${id}/events`);
  const eventTypes=[
    'investigation_created','phase_changed','hypotheses_generated','evidence_planned',
    'tool_selected','tool_completed','round_started','evidence_collected',
    'hypothesis_updated','sufficiency_evaluated','verdict_generated',
    'investigation_completed','investigation_failed','planner_completed'
  ];
  eventTypes.forEach(type=>eventSource.addEventListener(type,event=>{
    const payload=JSON.parse(event.data);
    render(payload.snapshot);
  }));
  eventSource.onerror=()=>{
    if(eventSource&&eventSource.readyState===EventSource.CLOSED){
      runButton.disabled=false;runButton.textContent='Run again';
    }
  };
}

runButton.addEventListener('click',async()=>{
  runButton.disabled=true;runButton.textContent='Investigating…';
  document.getElementById('verdict').textContent='OpsMind is interpreting the incident and preparing competing hypotheses.';
  try{
    const response=await fetch('/api/v1/investigations',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        problem:'Why is HF-PROD-02 not forwarding logs to the Splunk indexer cluster?',
        environment:'Production',
        priority:'High'
      })
    });
    if(!response.ok){
      const detail=await response.text();
      throw new Error(`HTTP ${response.status}: ${detail}`);
    }
    const data=await response.json();
    render(data);
    connectEvents(data.investigation_id);
  }catch(error){
    document.getElementById('currentPhase').textContent='Failed';
    document.getElementById('verdict').textContent=`Investigation failed: ${error.message}`;
    runButton.disabled=false;runButton.textContent='Retry';
    console.error(error);
  }
});

document.getElementById('graphButton').addEventListener('click',()=>{
  renderGraph(lastSnapshot);
  document.getElementById('graphModal').classList.add('open');
});
document.getElementById('closeGraph').addEventListener('click',()=>document.getElementById('graphModal').classList.remove('open'));
document.getElementById('judgeMode').addEventListener('click',()=>document.getElementById('judgeOverlay').classList.add('open'));
document.getElementById('closeJudge').addEventListener('click',()=>document.getElementById('judgeOverlay').classList.remove('open'));

document.querySelectorAll('.nav-item').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('.nav-item').forEach(x=>x.classList.remove('active'));
  button.classList.add('active');
  if(button.dataset.section==='graph')document.getElementById('graphButton').click();
}));
