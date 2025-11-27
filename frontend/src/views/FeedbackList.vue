<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Feedback Management</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Search Bar -->
      <div class="actions-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Cari kandidat..."
          class="search-input"
        />
      </div>

      <!-- ============================== -->
      <!-- FEEDBACK - BELUM DIREVIEW -->
      <!-- ============================== -->
      <p class="dashboard-subtitle">Kandidat Yang Siap Direview ({{ filteredBelumReview.length }})</p>
      <div class="table-scroll-wrapper">
        <table class="request-table">
          <thead>
            <tr>
              <th>No</th>
              <th>Candidate ID</th>
              <th>Nama</th>
              <th>Email</th>
              <th>Telepon</th>
              <th>Domisili</th>
              <th>Status</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(candidate, index) in filteredBelumReview"
              :key="candidate.candidate_id"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ candidate.candidate_id }}</td>
              <td>{{ candidate.name }}</td>
              <td>{{ candidate.email || '-' }}</td>
              <td>{{ candidate.telepon || '-' }}</td>
              <td>{{ candidate.domisili || '-' }}</td>
              <td>
                <span :class="getStatusClass(candidate.status)">
                  {{ formatStatus(candidate.status) }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="btn-edit" @click="goToAddFeedback(candidate)">
                  ➕ Review
                </button>
              </td>
            </tr>
            <tr v-if="filteredBelumReview.length === 0">
              <td colspan="8" class="text-center">
                Tidak ada kandidat yang siap direview.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <br />

      <!-- ============================================ -->
      <!-- FEEDBACK HISTORY - SUDAH DIREVIEW -->
      <!-- ============================================ -->
      <h2 class="dashboard-subtitle">Feedback Yang Sudah Diberikan ({{ filteredSudahReview.length }})</h2>
      <div class="table-scroll-wrapper">
        <table class="request-table">
          <thead>
            <tr>
              <th>No</th>
              <th>Candidate ID</th>
              <th>Nama</th>
              <th>Email</th>
              <th>Telepon</th>
              <th>Domisili</th>
              <th>Rating</th>
              <th>Komentar</th>
              <th>Tanggal</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(feedback, index) in filteredSudahReview"
              :key="feedback.id"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ feedback.candidate_id }}</td>
              <td>{{ feedback.candidate_name }}</td>
              <td>{{ feedback.candidate_email || '-' }}</td>
              <td>{{ feedback.candidate_telepon || '-' }}</td>
              <td>{{ feedback.candidate_domisili || '-' }}</td>
              <td>
                <span class="rating-badge">⭐ {{ feedback.rating }}</span>
              </td>
              <td class="comment-cell" @click="showFeedbackDetail(feedback.id)" style="cursor: pointer;">
                {{ truncateComment(feedback.comment) }}
              </td>
              <td>{{ formatDate(feedback.created_at) }}</td>
              <td class="actions-cell">
                <button @click="goToEditFeedback(feedback)" class="btn-edit-small">✏️ Edit</button>
                <button @click="deleteFeedback(feedback.id)" class="btn-delete-small">🗑️ Hapus</button>
              </td>
            </tr>
            <tr v-if="filteredSudahReview.length === 0">
              <td colspan="10" class="text-center">
                Belum ada feedback yang diberikan.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Feedback Detail Modal -->
      <div v-if="showDetailModal" class="modal-overlay">
        <div class="modal">
          <h3>Detail Feedback</h3>
          <div v-if="selectedFeedback" class="feedback-detail">
            <div class="detail-row">
              <strong>Candidate ID:</strong> {{ selectedFeedback.candidate.id }}
            </div>
            <div class="detail-row">
              <strong>Kandidat:</strong> {{ selectedFeedback.candidate.name }}
            </div>
            <div class="detail-row">
              <strong>Email:</strong> {{ selectedFeedback.candidate.email || '-' }}
            </div>
            <div class="detail-row">
              <strong>Telepon:</strong> {{ selectedFeedback.candidate.telepon || '-' }}
            </div>
            <div class="detail-row">
              <strong>Domisili:</strong> {{ selectedFeedback.candidate.domisili || '-' }}
            </div>
            <div class="detail-row">
              <strong>Status:</strong> {{ formatStatus(selectedFeedback.candidate.status) }}
            </div>
            <div class="detail-row">
              <strong>Rating:</strong> ⭐ {{ selectedFeedback.rating }}
            </div>
            <div class="detail-row">
              <strong>Komentar:</strong>
              <p class="comment-full">{{ selectedFeedback.comment }}</p>
            </div>
            <div class="detail-row">
              <strong>Diberikan oleh:</strong> {{ selectedFeedback.given_by.name }} ({{ selectedFeedback.given_by.role }})
            </div>
            <div class="detail-row">
              <strong>Tanggal:</strong> {{ formatDate(selectedFeedback.created_at) }}
            </div>
          </div>
          <div class="modal-actions">
            <button @click="closeDetailModal" class="btn-close">Tutup</button>
          </div>
        </div>
      </div>

      <!-- Alert -->
      <div v-if="showAlert" class="alert-overlay">
        <div class="alert-box">
          <p>{{ alertMessage }}</p>
          <button @click="closeAlert">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'FeedbackList',
  data() {
    const user = JSON.parse(localStorage.getItem('user')) || {};
    return {
      candidates: [],
      feedbacks: [],
      searchQuery: '',
      token: user.token || '',
      
      showDetailModal: false,
      selectedFeedback: null,
      
      showAlert: false,
      alertMessage: ''
    };
  },
  computed: {
    filteredBelumReview() {
      const q = this.searchQuery.toLowerCase();
      return this.candidates.filter(candidate => 
        !candidate.already_feedback && (
          candidate.name.toLowerCase().includes(q) ||
          candidate.candidate_id.toString().includes(q) ||
          (candidate.email && candidate.email.toLowerCase().includes(q)) ||
          (candidate.telepon && candidate.telepon.toLowerCase().includes(q)) ||
          (candidate.domisili && candidate.domisili.toLowerCase().includes(q)) ||
          candidate.status.toLowerCase().includes(q)
        )
      );
    },
    
    filteredSudahReview() {
      const q = this.searchQuery.toLowerCase();
      return this.feedbacks.filter(feedback =>
        (feedback.candidate_name && feedback.candidate_name.toLowerCase().includes(q)) ||
        feedback.candidate_id.toString().includes(q) ||
        (feedback.candidate_email && feedback.candidate_email.toLowerCase().includes(q)) ||
        (feedback.candidate_telepon && feedback.candidate_telepon.toLowerCase().includes(q)) ||
        (feedback.candidate_domisili && feedback.candidate_domisili.toLowerCase().includes(q)) ||
        (feedback.comment && feedback.comment.toLowerCase().includes(q))
      );
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      try {
        console.log("Loading feedback data...");
        
        // Load semua candidate untuk feedback (endpoint baru)
        const candidatesRes = await axios.get(
          'http://localhost:5000/candidates/for-feedback',
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );
        console.log("Candidates data:", candidatesRes.data);
        this.candidates = candidatesRes.data.data || [];

        // Load existing feedbacks
        const feedbacksRes = await axios.get(
          'http://localhost:5000/feedbacks',
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );
        console.log("Feedbacks data:", feedbacksRes.data);
        this.feedbacks = feedbacksRes.data.data || [];
        
      } catch (error) {
        console.error('Error loading data:', error);
        console.error('Error response:', error.response);
        this.showCustomAlert('Gagal memuat data feedback: ' + (error.response?.data?.message || error.message));
      }
    },

    goToAddFeedback(candidate) {
      this.$router.push({
        name: 'AddFeedback',
        params: { candidateId: candidate.candidate_id },
        query: { 
          candidateName: candidate.name,
          candidateEmail: candidate.email,
          candidateTelepon: candidate.telepon,
          candidateDomisili: candidate.domisili,
          candidateStatus: candidate.status
        }
      });
    },

    goToEditFeedback(feedback) {
      console.log('Navigating to edit feedback:', feedback)
      this.$router.push({
        name: 'EditFeedback',
        params: { id: feedback.id }
      });
    },

    async showFeedbackDetail(feedbackId) {
      try {
        const res = await axios.get(
          `http://localhost:5000/feedbacks/${feedbackId}`,
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );
        this.selectedFeedback = res.data.data;
        this.showDetailModal = true;
      } catch (error) {
        console.error('Error loading feedback detail:', error);
        this.showCustomAlert('Gagal memuat detail feedback: ' + (error.response?.data?.message || error.message));
      }
    },

    closeDetailModal() {
      this.showDetailModal = false;
      this.selectedFeedback = null;
    },

    async deleteFeedback(feedbackId) {
      if (!confirm('Apakah Anda yakin ingin menghapus feedback ini?')) {
        return;
      }
      
      try {
        await axios.delete(
          `http://localhost:5000/feedbacks/${feedbackId}`,
          { 
            headers: { Authorization: `Bearer ${this.token}` } 
          }
        );
        
        this.showCustomAlert('Feedback berhasil dihapus!');
        await this.loadData();
      } catch (error) {
        console.error('Error deleting feedback:', error);
        this.showCustomAlert('Gagal menghapus feedback: ' + (error.response?.data?.message || error.message));
      }
    },

    showCustomAlert(message) {
      this.alertMessage = message;
      this.showAlert = true;
    },

    closeAlert() {
      this.showAlert = false;
    },

    getStatusClass(status) {
      const statusMap = {
        'Unconfirmed': 'status-pending',
        'Onboarding': 'status-lulus',
        'Not Available': 'status-tidak-lulus',
        'ASAP': 'status-pending',
        'Few Weeks': 'status-pending',
        '1 Month Notice': 'status-pending',
        '2 Month Notice': 'status-pending'
      };
      return statusMap[status] || 'status-pending';
    },

    formatStatus(status) {
      const statusMap = {
        'Unconfirmed': 'Belum Dikonfirmasi',
        'Onboarding': 'Onboarding',
        'Not Available': 'Tidak Tersedia',
        'ASAP': 'ASAP',
        'Few Weeks': 'Beberapa Minggu',
        '1 Month Notice': '1 Month Notice',
        '2 Month Notice': '2 Month Notice'
      };
      return statusMap[status] || status;
    },

    truncateComment(comment) {
      if (!comment) return '-';
      return comment.length > 50 ? comment.substring(0, 50) + '...' : comment;
    },

    formatDate(isoString) {
      if (!isoString) return '-';
      const date = new Date(isoString);
      return date.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    }
  }
};
</script>

<style scoped>
/* ===== TABLE SCROLL WRAPPER ===== */
.table-scroll-wrapper {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  border-radius: 8px;
  -webkit-overflow-scrolling: touch;
  margin-top: 10px;
}

.table-scroll-wrapper::-webkit-scrollbar {
  height: 8px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb {
  background: #caa7a7;
  border-radius: 4px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a26060;
}

.dashboard-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 100px 0 40px;
}

.dashboard-container {
  width: 90%;
  max-width: 1200px;
  color: #333;
  font-family: 'Poppins', sans-serif;
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* Header */
.dashboard-title {
  font-size: 32px;
  font-weight: 700;
  color: #7a3e3e;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
  margin-bottom: 15px;
}

.dashboard-subtitle {
  font-size: 24px;
  font-weight: 700;
  color: #7a3e3e;
}

/* Actions Bar */
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-input {
  width: 300px;
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 14px;
}

/* Table Styling */
.request-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e0d5d5;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  min-width: 900px; /* Minimum width untuk table yang lebih lebar */
}

.request-table th,
.request-table td {
  padding: 12px 10px;
  text-align: center;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
}

.request-table th {
  background-color: #a26060;
  color: #fff;
  font-weight: 600;
}

.request-table tbody tr:nth-child(even) {
  background-color: #faf6f6;
}

.request-table tbody tr:hover {
  background-color: #f5eaea;
  transition: 0.3s;
}

.text-center {
  text-align: center;
}

/* Button Actions */
.actions-cell {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.btn-edit {
  background: #43a032;
  color: #fff;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
}

.btn-edit:hover {
  background: #2e7d1f;
}

/* TOMBOL EDIT/HAPUS KECIL UNTUK TABEL KEDUA */
.btn-edit-small, .btn-delete-small {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
}

.btn-edit-small {
  background-color: #ffc107;
  color: black;
}

.btn-edit-small:hover {
  background-color: #e0a800;
}

.btn-delete-small {
  background-color: #dc3545;
  color: white;
}

.btn-delete-small:hover {
  background-color: #c82333;
}

/* ===== STATUS BADGE STYLES ===== */
.status-lulus {
  background-color: #0c8c41;
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.status-tidak-lulus {
  background-color: #ab2929;
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.status-pending {
  background-color: #f39c12;
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

/* Rating Badge */
.rating-badge {
  background: #ffd700;
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 13px;
}

/* Comment Cell */
.comment-cell {
  max-width: 200px;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.modal h3 {
  margin-bottom: 20px;
  color: #7a3e3e;
  text-align: center;
}

.feedback-detail {
  text-align: left;
}

.detail-row {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.detail-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.comment-full {
  margin-top: 5px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
  border-left: 4px solid #a26060;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.btn-close, .btn-primary, .btn-secondary {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-close, .btn-primary {
  background: #a26060;
  color: white;
}

.btn-close:hover, .btn-primary:hover:not(:disabled) {
  background: #7a3e3e;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

/* Alert Styles */
.alert-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.alert-box {
  background: white;
  padding: 20px;
  border-radius: 12px;
  width: 300px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.alert-box button {
  background: #a26060;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  margin-top: 10px;
}
</style>