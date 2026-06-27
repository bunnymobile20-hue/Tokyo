import React, { useState, useEffect } from 'react';
import { apiFetch } from '../lib/api';

export default function DesktopAgentPage() {
    const [status, setStatus] = useState<any>(null);
    const [tasks, setTasks] = useState<any>([]);
    const [error, setError] = useState<string | null>(null);

    const fetchStatus = async () => {
        try {
            const data = await apiFetch('/tokyo/desktop-agent/status');
            setStatus(data);
        } catch (e: any) {
            console.error("Failed to fetch status", e);
        }
    };

    const fetchTasks = async () => {
        try {
            const data: any = await apiFetch('/tokyo/desktop-agent/tasks');
            if (data && data.completed) {
                setTasks(data.completed.slice(0, 10)); // Just show recent 10
            }
        } catch (e: any) {
            console.error("Failed to fetch tasks", e);
        }
    };

    useEffect(() => {
        fetchStatus();
        fetchTasks();
        const interval = setInterval(() => {
            fetchStatus();
            fetchTasks();
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    const executeTask = async (action_type: string, payload: any) => {
        setError(null);
        try {
            await apiFetch('/tokyo/operator/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    command: `Execute ${action_type}`,
                    action_type,
                    payload
                })
            });
            fetchTasks();
        } catch (e: any) {
            setError(e.message || "Failed to execute task");
        }
    };

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">Desktop Agent (MacBook)</h1>
            
            <div className="bg-white dark:bg-gray-800 rounded shadow p-4 mb-6 border-l-4 border-blue-500">
                <h2 className="text-lg font-semibold mb-2">Agent Status</h2>
                {status ? (
                    <div>
                        <p>
                            <span className="font-semibold">State: </span> 
                            <span className={status.online ? 'text-green-500 font-bold' : 'text-red-500 font-bold'}>
                                {status.online ? '🟢 ONLINE' : '🔴 OFFLINE'}
                            </span>
                        </p>
                        <p><span className="font-semibold">Last Heartbeat:</span> {status.last_heartbeat ? new Date(status.last_heartbeat).toLocaleString() : 'Never'}</p>
                        <p><span className="font-semibold">Workspace:</span> {status.workspace || 'N/A'}</p>
                        <p><span className="font-semibold">Pending Tasks:</span> {status.pending_tasks_count}</p>
                    </div>
                ) : (
                    <p>Loading status...</p>
                )}
            </div>

            {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4">{error}</div>}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-white dark:bg-gray-800 rounded shadow p-4">
                    <h3 className="font-semibold mb-4">File Operations (Sandbox)</h3>
                    <div className="space-x-2">
                        <button 
                            onClick={() => executeTask('create_folder', {folder_name: 'teste'})}
                            className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600">
                            Create Folder "teste"
                        </button>
                        <button 
                            onClick={() => executeTask('quarantine_folder', {folder_name: 'teste'})}
                            className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
                            Quarantine "teste"
                        </button>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded shadow p-4">
                    <h3 className="font-semibold mb-4">Web Operations (Playwright)</h3>
                    <div className="space-x-2">
                        <button 
                            onClick={() => executeTask('open_url', {url: 'https://example.com'})}
                            className="bg-purple-500 text-white px-3 py-1 rounded hover:bg-purple-600">
                            Open Site
                        </button>
                        <button 
                            onClick={() => executeTask('extract_text', {url: 'https://example.com'})}
                            className="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600">
                            Extract Text
                        </button>
                    </div>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded shadow p-4">
                <h3 className="font-semibold mb-4">Recent Task Logs</h3>
                {tasks.length > 0 ? (
                    <div className="space-y-4">
                        {tasks.map((task: any) => (
                            <div key={task.task_id} className="border-b pb-2">
                                <p className="font-medium">{task.command} <span className={`text-sm ${task.status === 'completed' ? 'text-green-500' : 'text-red-500'}`}>[{task.status}]</span></p>
                                <p className="text-xs text-gray-500">{new Date(task.updated_at).toLocaleString()}</p>
                                {task.result && (
                                    <pre className="text-xs bg-gray-100 dark:bg-gray-900 p-2 mt-1 rounded overflow-x-auto">
                                        {JSON.stringify(task.result, null, 2)}
                                    </pre>
                                )}
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-sm text-gray-500">No tasks completed yet.</p>
                )}
            </div>
        </div>
    );
}
