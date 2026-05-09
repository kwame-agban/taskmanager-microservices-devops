import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Task {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  ownerUsername: string;
}

export interface TaskRequest {
  title: string;
  description: string;
}

@Injectable({ providedIn: 'root' })
export class TaskService {
  private http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/api/tasks`;

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('taskmanager_token') || '';

    return new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
  }

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(this.apiUrl, {
      headers: this.getAuthHeaders()
    });
  }

  createTask(payload: TaskRequest): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, payload, {
      headers: this.getAuthHeaders()
    });
  }

  completeTask(id: number): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${id}/complete`, {}, {
      headers: this.getAuthHeaders()
    });
  }

  deleteTask(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, {
      headers: this.getAuthHeaders()
    });
  }
}
