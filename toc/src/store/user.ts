import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('toc_user', () => {
  const token = ref<string>(localStorage.getItem('tiku_toc_token') || '');
  const username = ref<string>(localStorage.getItem('tiku_toc_username') || '');
  const nickname = ref<string>(localStorage.getItem('tiku_toc_nickname') || '');

  function setToken(newToken: string, name: string, newNickname?: string) {
    token.value = newToken;
    username.value = name;
    if (newNickname !== undefined) nickname.value = newNickname;
    localStorage.setItem('tiku_toc_token', newToken);
    localStorage.setItem('tiku_toc_username', name);
    if (newNickname !== undefined) localStorage.setItem('tiku_toc_nickname', newNickname || '');
  }

  function setNickname(newNickname: string) {
    nickname.value = newNickname;
    localStorage.setItem('tiku_toc_nickname', newNickname || '');
  }

  function logout() {
    token.value = '';
    username.value = '';
    nickname.value = '';
    localStorage.removeItem('tiku_toc_token');
    localStorage.removeItem('tiku_toc_username');
    localStorage.removeItem('tiku_toc_nickname');
  }

  return { token, username, nickname, setToken, setNickname, logout };
});
