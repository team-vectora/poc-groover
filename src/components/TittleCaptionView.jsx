"use client";
import Image from 'next/image';
import React , { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {faCodeFork} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import Link from "next/link";

const TittleCaption = ({ onPlaySong, onPlayActivePage, onExport, onFork, t, setLang, lang, title }) => {

  const [username, setUsername] = useState('');
  const router = useRouter();

  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) {
      setUsername(storedUsername);
    }
  }, []);

  const userData = {
    name: username,
    role: "Produtor Musical",
    avatar: ""
  };



  return (
    <header className="app-header">
      <div className="header-logo-container">
        <Image src="/img/groover_logo.png" alt="Logo" width={100} height={200} />
        <h1 className="header-logo-text">GROOVER</h1>
        <h2 className="header-logo-text">{title}</h2>
      </div>
      <div className="header-user-profile">
        <div className="header-actions">
          <button className="header-button" onClick={onPlaySong}>
            ▶ {t("playSong") /* exemplo: "TOCAR MÚSICA" */}
          </button>
          <button className="header-button" onClick={onPlayActivePage}>
            ▶ {t("playPage") /* exemplo: "TOCAR PÁGINA" */}
          </button>
          <button className="header-button" onClick={onExport}>
            ↕ {t("export")}
          </button>

          <button className="header-button" onClick={onFork}>
            <FontAwesomeIcon icon={faCodeFork} /> {t("Fork")}
          </button>


        </div>
        <div className="language-switcher">
          <button
            className="header-button"
            onClick={() => setLang(lang === "pt" ? "en" : "pt")}
            aria-label="Switch Language"
            title={lang === "pt" ? "Switch to English" : "Mudar para Português"}
          >
            {lang === "pt" ? "🇧🇷" : "🇺🇸"}
          </button>
        </div>
        <div className="header-user-info">
          <h3 className="header-user-name">{userData.name}</h3>
          <span className="header-user-role">{userData.role}</span>
        </div>
        {userData.avatar && (
          <img
            src={userData.avatar}
            alt="Avatar"
            className="header-user-avatar"
          />
        )}
      </div>
    </header>
  );
};

export default TittleCaption;
