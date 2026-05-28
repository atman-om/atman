import { Nav } from '../../components/Nav';
import ChatClient from './ChatClient';
export default function Page() { return <main className="shell"><Nav /><h1>Atman Chatbot</h1><p>Remote Qwen + canonical/RAG evidence + hidden/source/scholar citation modes.</p><ChatClient /></main>; }
