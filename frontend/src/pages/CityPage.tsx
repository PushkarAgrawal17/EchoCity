import { useEffect } from 'react';
import { FiActivity, FiTerminal, FiUser, FiShare2, FiTrendingUp } from 'react-icons/fi';
import { DesktopBackground } from '../components/desktop/DesktopBackground';
import { DraggableWindow } from '../components/desktop/DraggableWindow';
import { Dock } from '../components/desktop/Dock';
import { HorizonHeader } from '../components/horizon/HorizonHeader';
import { StreamOfConsciousnessWindow } from '../components/streamOfConsciousness/StreamOfConsciousnessWindow';
import { SynapticOverrideWindow } from '../components/terminal/SynapticOverrideWindow';
import { CitizenProfileWindow } from '../components/citizenProfile/CitizenProfileWindow';
import { RelationshipGraphWindow } from '../components/relationshipGraph/RelationshipGraphWindow';
import { TemporalLoomWindow } from '../components/temporalLoom/TemporalLoomWindow';
import { useAgentStore } from '../store/agentStore';
import { useWorldStore } from '../store/worldStore';
import { useWorldClock } from '../hooks/useWorldClock';

export function CityPage() {
  const loadAgents = useAgentStore((s) => s.loadAgents);
  const loadWorld = useWorldStore((s) => s.loadWorld);

  useEffect(() => {
    loadAgents();
    loadWorld();
  }, [loadAgents, loadWorld]);

  useWorldClock();

  return (
    <div className="relative h-screen w-screen overflow-hidden bg-void">
      <DesktopBackground />

      <div className="relative z-10 flex h-full flex-col">
        <HorizonHeader />

        <div className="relative flex-1">
          <DraggableWindow id="streamOfConsciousness" title="Stream of Consciousness" icon={<FiActivity size={12} className="text-echo-cyan" />}>
            <StreamOfConsciousnessWindow />
          </DraggableWindow>

          <DraggableWindow id="synapticOverride" title="Synaptic Override" icon={<FiTerminal size={12} className="text-echo-green" />}>
            <SynapticOverrideWindow />
          </DraggableWindow>

          <DraggableWindow id="citizenProfile" title="Citizen Profile" icon={<FiUser size={12} className="text-echo-amber" />}>
            <CitizenProfileWindow />
          </DraggableWindow>

          <DraggableWindow id="relationshipGraph" title="Relationship Graph" icon={<FiShare2 size={12} className="text-echo-cyan" />}>
            <RelationshipGraphWindow />
          </DraggableWindow>

          <DraggableWindow id="temporalLoom" title="Temporal Loom" icon={<FiTrendingUp size={12} className="text-echo-amber" />}>
            <TemporalLoomWindow />
          </DraggableWindow>

          <Dock />
        </div>
      </div>
    </div>
  );
}
