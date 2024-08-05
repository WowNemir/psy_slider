export interface ActiveSession {
    id: string;
    post_session_completed: boolean;
    pre_session_completed: boolean;
    share_uid: string;
    start_time: string;
    status: string;
  }
  
export interface Client {
    id: string;
    name: string;
    activeSession: ActiveSession | null;
  }
  // Ensure this is in the `types` file or wherever your interfaces are defined
export interface Choice {
    choice: string;
    client_id: string;
    id: string;
    question_id: string;
    session_id: string
    timestamp: string;
    user_id: string;
  }