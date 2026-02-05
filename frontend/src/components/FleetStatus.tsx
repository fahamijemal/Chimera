import React from 'react';

interface AgentStatus {
    id: string;
    name: string;
    role: 'Planner' | 'Worker' | 'Judge';
    info: string;
    status: 'active' | 'idle' | 'offline';
    wallet_balance: {
        eth: number;
        usdc: number;
    };
}

const FleetStatus: React.FC = () => {
    // Mock data for the prototype
    const agents: AgentStatus[] = [
        {
            id: 'agent-planner-01',
            name: 'Strategist Prime',
            role: 'Planner',
            info: 'Analyzing "Summer 2026" trends',
            status: 'active',
            wallet_balance: { eth: 0.05, usdc: 120.00 }
        },
        {
            id: 'agent-worker-01',
            name: 'Content Gen Alpha',
            role: 'Worker',
            info: 'Generating image for #ChimeraDrop',
            status: 'active',
            wallet_balance: { eth: 0.01, usdc: 15.50 }
        },
        {
            id: 'agent-worker-02',
            name: 'Social Interaction Bot',
            role: 'Worker',
            info: 'Replying to comments on Post #882',
            status: 'idle',
            wallet_balance: { eth: 0.01, usdc: 45.00 }
        },
        {
            id: 'agent-judge-cfo',
            name: 'The CFO',
            role: 'Judge',
            info: 'Monitoring transaction thresholds',
            status: 'active',
            wallet_balance: { eth: 0.10, usdc: 5000.00 }
        }
    ];

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-100 text-green-800';
            case 'idle': return 'bg-gray-100 text-gray-800';
            default: return 'bg-red-100 text-red-800';
        }
    };

    const getRoleBadge = (role: string) => {
        switch (role) {
            case 'Planner': return 'bg-purple-100 text-purple-800';
            case 'Worker': return 'bg-blue-100 text-blue-800';
            case 'Judge': return 'bg-yellow-100 text-yellow-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    }

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Fleet Status (Active Swarm)
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    Real-time health and financial status of active agents.
                </p>
            </div>
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Agent Name
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Role
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Current Activity
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Wallet Balance
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {agents.map((agent) => (
                            <tr key={agent.id}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="text-sm font-medium text-gray-900">{agent.name}</div>
                                    <div className="text-xs text-gray-500">{agent.id}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadge(agent.role)}`}>
                                        {agent.role}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {agent.info}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(agent.status)}`}>
                                        {agent.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                                    <div className="flex flex-col">
                                        <span>{agent.wallet_balance.usdc.toFixed(2)} USDC</span>
                                        <span className="text-xs text-gray-400">{agent.wallet_balance.eth.toFixed(4)} ETH</span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default FleetStatus;
