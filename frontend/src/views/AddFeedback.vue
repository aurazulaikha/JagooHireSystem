<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Header -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">Beri Feedback</h1>
        <div class="title-underline"></div>
      </div>

      <!-- Candidate Profile -->
      <div class="candidate-profile">
        <h3>Profil Kandidat</h3>
        <div class="profile-info">
          <div class="info-item">
            <strong>Nama:</strong> {{ candidateName }}
          </div>
          <div class="info-item">
            <strong>Posisi:</strong> {{ candidateRole }}
          </div>
        </div>
      </div>

      <!-- Feedback Form -->
      <form @submit.prevent="submitFeedback" class="feedback-form">
        <!-- Rating -->
        <div class="form-group">
          <label for="rating">⭐ Rating (Wajib)</label>
          <input
            type="number"
            id="rating"
            v-model="form.rating"
            min="0"
            max="5"
            step="0.1"
            placeholder="0.00 - 5.00"
            required
            class="form-input"
          >
          <small>Masukkan nilai antara 0.00 sampai 5.00</small>
        </div>

        <!-- Comment -->
        <div class="form-group">
          <label for="comment">💬 Komentar Feedback (Wajib)</label>
          <textarea
            id="comment"
            v-model="form.comment"
            rows="6"
            placeholder="Tulis evaluasi untuk kandidat..."
            required
            class="form-textarea"
          ></textarea>
          <small>Contoh: Technical skill, Communication, Recommendation</small>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button type="button" @click="goBack" class="btn-secondary">
            ← Kembali ke List
          </button>
          <button type="submit" :disabled="loading" class="btn-primary">
            {{ loading ? 'Menyimpan...' : '✅ Submit Feedback' }}
          </button>
        </div>
      </form>

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
  name: 'AddFeedback',
  data() {
    const user = JSON.parse(localStorage.getItem('user')) || {};
    return {
      candidateId: this.$route.params.candidateId,
      candidateName: this.$route.query.candidateName || '',
      candidateRole: this.$route.query.candidateRole || '',
      token: user.token || '',
      loading: false,
      
      form: {
        rating: '',
        comment: ''
      },
      
      showAlert: false,
      alertMessage: ''
    };
  },
  mounted() {
    if (!this.candidateId) {
      this.showCustomAlert('Candidate ID tidak ditemukan');
      this.goBack();
    }
  },
  methods: {
    async submitFeedback() {
      // Validation
      if (!this.form.rating || !this.form.comment) {
        this.showCustomAlert('Rating dan komentar wajib diisi');
        return;
      }

      const rating = parseFloat(this.form.rating);
      if (isNaN(rating) || rating < 0 || rating > 5) {
        this.showCustomAlert('Rating harus antara 0.00 sampai 5.00');
        return;
      }

      this.loading = true;

      try {
        await axios.post(
          'http://localhost:5000/feedbacks',
          {
            candidate_id: this.candidateId,
            rating: rating,
            comment: this.form.comment
          },
          {
            headers: { Authorization: `Bearer ${this.token}` }
          }
        );

        this.showCustomAlert('Feedback berhasil disimpan!');
        
        // Redirect back to list after success
        setTimeout(() => {
          this.$router.push({ name: 'FeedbackList' });
        }, 1500);

      } catch (error) {
        console.error('Error submitting feedback:', error);
        const message = error.response?.data?.message || 'Gagal menyimpan feedback';
        this.showCustomAlert(message);
      } finally {
        this.loading = false;
      }
    },

    goBack() {
      this.$router.push({ name: 'FeedbackList' });
    },

    showCustomAlert(message) {
      this.alertMessage = message;
      this.showAlert = true;
    },

    closeAlert() {
      this.showAlert = false;
    }
  }
};
</script>

<style scoped>
.dashboard-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 100px 0 40px;
}

.dashboard-container {
  width: 90%;
  max-width: 800px;
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

/* Candidate Profile */
.candidate-profile {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e0d5d5;
}

.candidate-profile h3 {
  color: #7a3e3e;
  margin-bottom: 15px;
  font-size: 20px;
}

.profile-info {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.info-item {
  font-size: 16px;
}

.info-item strong {
  color: #a26060;
}

/* Feedback Form */
.feedback-form {
  background: white;
  padding: 25px;
  border-radius: 12px;
  border: 1px solid #e0d5d5;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #7a3e3e;
  font-size: 16px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Poppins', sans-serif;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #a26060;
  box-shadow: 0 0 0 2px rgba(162, 96, 96, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.form-group small {
  display: block;
  margin-top: 5px;
  color: #666;
  font-size: 12px;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn-secondary {
  background: #ccc;
  color: #333;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
}

.btn-secondary:hover {
  background: #bbb;
}

.btn-primary {
  background: #43a032;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
}

.btn-primary:hover:not(:disabled) {
  background: #2e7d1f;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Alert */
.alert-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.alert-box {
  background: white;
  padding: 25px;
  border-radius: 12px;
  width: 350px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.alert-box p {
  margin-bottom: 20px;
  font-size: 16px;
}

.alert-box button {
  background: #a26060;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.alert-box button:hover {
  background: #7a3e3e;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-container {
    width: 95%;
  }
  
  .profile-info {
    flex-direction: column;
    gap: 10px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .btn-secondary,
  .btn-primary {
    width: 100%;
  }
}
</style>