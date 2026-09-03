import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('toc_user', () => {
  const token = ref<string>(localStorage.getItem('tiku_toc_token') || '');
  const username = ref<string>(localStorage.getItem('tiku_toc_username') || '');

  function setToken(newToken: string, name: string) {
    token.value = newToken;
    username.value = name;
    localStorage.setItem('tiku_toc_token', newToken);
    localStorage.setItem('tiku_toc_username', name);
  }

  function logout() {
    token.value = '';
    username.value = '';
    localStorage.removeItem('tiku_toc_token');
    localStorage.removeItem('tiku_toc_username');
  }

  return { token, username, setToken, logout };
});
