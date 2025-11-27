<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1 class="dashboard-title">Professional Test</h1>
        <div class="title-underline"></div>
      </div>

      <div class="form-container">
        <form @submit.prevent="testProfessional">
          <div class="form-group">
            <label>Nama Kandidat</label>
            <input v-model="form.candidate_name" readonly />
          </div>

          <div class="form-group">
            <label>Tanggal Tes</label>
            <input v-model="form.test_date" type="date" required />
          </div>

          <div class="form-group" v-if="form.aptitude_score">
            <label>Aptitude Score</label>
            <input v-model="form.aptitude_score" type="number" step="0.01" readonly class="readonly-field" />
          </div>

          <div class="form-group">
            <label>Programming Fundamentals</label>
            <input v-model="form.programming_fundamentals" type="number" step="0.01" min="0" max="100" required />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Software Engineering</label>
              <select v-model="form.software_engineering" required>
                <option value="incompetent">Incompetent</option>
                <option value="developing">Developing</option>
                <option value="advance">Advance</option>
              </select>
            </div>

            <div class="form-group">
              <label>Portfolio Evaluation</label>
              <select v-model="form.portfolio_eval" required>
                <option value="incompetent">Incompetent</option>
                <option value="developing">Developing</option>
                <option value="advance">Advance</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Communication</label>
              <select v-model="form.communication" required>
                <option value="incompetent">Incompetent</option>
                <option value="developing">Developing</option>
                <option value="advance">Advance</option>
              </select>
            </div>

            <div class="form-group">
              <label>Adaptability</label>
              <select v-model="form.adaptability" required>
                <option value="incompetent">Incompetent</option>
                <option value="developing">Developing</option>
                <option value="advance">Advance</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Discipline</label>
              <select v-model="form.discipline" required>
                <option value="incompetent">Incompetent</option>
                <option value="developing">Developing</option>
                <option value="advance">Advance</option>
              </select>
            </div>

            <div class="form-group">
              <label>Commitment</label>
              <select v-model="form.commitment" required>
                <option value="incompetent">Incompetent</option>
                <option value="developing">Developing</option>
                <option value="advance">Advance</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Final Result</label>
            <select v-model="form.final_result" required>
              <option value="lulus">Lulus</option>
              <option value="tidak_lulus">Tidak Lulus</option>
            </select>
          </div>

          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="form.notes" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-add">{{ mode === 'edit' ? 'Update' : 'Simpan' }}</button>
            <button type="button" class="btn-cancel" @click="goBack">
              Batal
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Pop-up Notification -->
    <transition name="fade">
      <div v-if="showPopup" :class="['popup', popupType]">
        <p>{{ popupMessage }}</p>
      </div>
    </transition>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "ProfessionalTestForm",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    const selected = JSON.parse(localStorage.getItem("selectedCandidate")) || {};
    
    return {
      form: {
        request_candidate_id: selected.request_candidate_id || "",
        candidate_name: selected.candidate_name || "",
        test_date: selected.test_date 
          ? new Date(selected.test_date).toISOString().substr(0, 10)
          : "",
        aptitude_score: selected.aptitude_score || "",
        programming_fundamentals: selected.programming_fundamentals || "",
        software_engineering: selected.software_engineering || "",
        portfolio_eval: selected.portfolio_eval || "",
        communication: selected.communication || "",
        adaptability: selected.adaptability || "",
        discipline: selected.discipline || "",
        commitment: selected.commitment || "",
        final_result: selected.final_result || "",
        notes: selected.notes || "",
      },
      mode: selected.mode || "add",
      token: user.token || "",
      showPopup: false,
      popupMessage: "",
      popupType: "",
    };
  },
  methods: {
    async testProfessional() {
      try {
        const payload = {
          request_candidate_id: this.form.request_candidate_id,
          test_date: this.form.test_date,
          programming_fundamentals: this.form.programming_fundamentals ? parseFloat(this.form.programming_fundamentals) : null,
          software_engineering: this.form.software_engineering,
          portfolio_eval: this.form.portfolio_eval,
          communication: this.form.communication,
          adaptability: this.form.adaptability,
          discipline: this.form.discipline,
          commitment: this.form.commitment,
          final_result: this.form.final_result,
          notes: this.form.notes,
        };

        await axios.post(
          "http://localhost:5000/professional_tests",
          payload,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        const message = this.mode === 'edit' 
          ? "Data professional test berhasil diupdate!" 
          : "Data professional test berhasil disimpan!";
        
        this.showNotification(message, "success");
        setTimeout(() => this.$router.push("/professional-tests"), 1800);
      } catch (error) {
        console.error(error);
        const msg = error.response?.data?.message || "Gagal menyimpan data professional test.";
        this.showNotification(msg, "error");
      }
    },
    
    showNotification(message, type) {
      this.popupMessage = message;
      this.popupType = type;
      this.showPopup = true;
      setTimeout(() => {
        this.showPopup = false;
      }, 2000);
    },
    
    goBack() {
      this.$router.push("/professional-tests");
    },
  },
};
</script>

<style scoped>
.dashboard-wrapper {
  background: linear-gradient(180deg, #f9f3f3, #fff);
  min-height: 100vh;
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 80px 60px;
  box-sizing: border-box;
  position: relative;
}

.dashboard-container {
  width: 100%;
  max-width: 800px;
  color: #333;
  font-family: "Poppins", sans-serif;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 25px;
}

.dashboard-header {
  text-align: left;
  width: 100%;
}

.dashboard-title {
  font-size: 32px;
  font-weight: 700;
  color: #7a3e3e;
  margin-bottom: 10px;
  text-align: left;
}

.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
  margin-bottom: 25px;
}

.form-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 25px;
  width: 100%;
  max-width: 700px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

label {
  font-weight: 600;
  margin-bottom: 6px;
  color: #7a3e3e;
}

input,
select,
textarea {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 14px;
  font-family: inherit;
}

input[readonly] {
  background-color: #f5f5f5;
  color: #666;
}

.readonly-note {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  font-style: italic;
}

textarea {
  resize: none;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-add {
  background: #a26060;
  color: #fff;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}

.btn-add:hover {
  background: #7a3e3e;
}

.btn-cancel {
  background: #ccc;
  color: #333;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}

.btn-cancel:hover {
  background: #999;
}

/* Popup */
.popup {
  position: fixed;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  padding: 16px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 15px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
  color: #fff;
  z-index: 1000;
  opacity: 0.95;
}

.popup.success {
  background-color: #4caf50;
}

.popup.error {
  background-color: #f44336;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>