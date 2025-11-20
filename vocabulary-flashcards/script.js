document.addEventListener('DOMContentLoaded', () => {
  const cardContainer = document.getElementById('card-container');
  const card = document.querySelector('.card');
  const wordDisplay = document.getElementById('word-display');
  const analysisContent = document.getElementById('analysis-content');
  const currentIndexDisplay = document.getElementById('current-index');
  const totalCountDisplay = document.getElementById('total-count');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');

  let words = [];
  let currentIndex = 0;

  // Quiz Elements
  const tabs = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  const quizQuestion = document.getElementById('quiz-question');
  const quizOptions = document.getElementById('quiz-options');
  const quizFeedback = document.getElementById('quiz-feedback');
  const nextQuestionBtn = document.getElementById('next-question-btn');
  const quizScoreDisplay = document.getElementById('quiz-score');
  const downloadMistakesBtn = document.getElementById('download-mistakes-btn');

  let quizScore = 0;
  let currentQuestion = null;
  let mistakes = [];

  // Initialize
  loadMistakes();

  // Fetch words data
  fetch('data/words.json')
    .then(response => response.json())
    .then(data => {
      // Shuffle words for random order
      words = data.sort(() => Math.random() - 0.5);
      totalCountDisplay.textContent = words.length;
      loadCard(currentIndex);
    })
    .catch(error => {
      console.error('Error loading words:', error);
      wordDisplay.textContent = "Error loading data";
    });

  // Flip card interaction
  cardContainer.addEventListener('click', () => {
    // Only flip if no text is selected to avoid flipping while selecting text
    const selection = window.getSelection();
    if (selection.toString().length === 0) {
      card.classList.toggle('is-flipped');
    }
  });

  // Navigation
  prevBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent flip
    if (currentIndex > 0) {
      currentIndex--;
      resetCard();
      setTimeout(() => loadCard(currentIndex), 300);
    }
  });

  nextBtn.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent flip
    if (currentIndex < words.length - 1) {
      currentIndex++;
      resetCard();
      setTimeout(() => loadCard(currentIndex), 300);
    }
  });

  // Tab Switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      tab.classList.add('active');
      document.getElementById(`${tab.dataset.tab}-section`).classList.add('active');

      if (tab.dataset.tab === 'quiz' && !currentQuestion) {
        generateQuestion();
      }
    });
  });

  // Quiz Logic
  nextQuestionBtn.addEventListener('click', generateQuestion);
  downloadMistakesBtn.addEventListener('click', downloadMistakes);

  // Click quiz word to go to Learn tab
  quizQuestion.addEventListener('click', () => {
    if (!currentQuestion || !currentQuestion.target) return;

    const wordToFind = currentQuestion.target.word;
    const index = words.findIndex(w => w.word === wordToFind);

    if (index !== -1) {
      currentIndex = index;
      loadCard(currentIndex);

      // Switch to Learn tab
      tabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      // Find Learn tab button
      const learnTabBtn = document.querySelector('.tab-btn[data-tab="learn"]');
      if (learnTabBtn) learnTabBtn.classList.add('active');

      document.getElementById('learn-section').classList.add('active');
    }
  });

  function generateQuestion() {
    try {
      if (words.length < 4) return;

      // Reset UI
      quizOptions.innerHTML = '';
      quizFeedback.classList.remove('show');
      quizFeedback.innerHTML = '';
      nextQuestionBtn.style.display = 'none';

      // Clear previous reference if any
      const existingRef = document.getElementById('quiz-reference');
      if (existingRef) existingRef.remove();

      // Pick target word
      const targetIndex = Math.floor(Math.random() * words.length);
      const targetWord = words[targetIndex];

      // Select Meaning (Prioritize Less Common)
      let selectedMeaning = null;
      if (targetWord.analysis && targetWord.analysis.less_common_meanings && targetWord.analysis.less_common_meanings.length > 0) {
        // 70% chance to pick a less common meaning if available
        if (Math.random() < 0.7) {
          const randIdx = Math.floor(Math.random() * targetWord.analysis.less_common_meanings.length);
          selectedMeaning = targetWord.analysis.less_common_meanings[randIdx];
        }
      }

      // Fallback to most common
      if (!selectedMeaning && targetWord.analysis && targetWord.analysis.most_common_meaning) {
        selectedMeaning = targetWord.analysis.most_common_meaning;
      }

      // Safety check
      if (!selectedMeaning) {
        // Try another word if this one has no data
        // Use setTimeout to avoid recursion stack overflow
        setTimeout(generateQuestion, 0);
        return;
      }

      // Pick 3 distractors
      const distractors = [];
      let attempts = 0;
      while (distractors.length < 3 && attempts < 50) {
        const idx = Math.floor(Math.random() * words.length);
        if (idx !== targetIndex && !distractors.includes(words[idx])) {
          distractors.push(words[idx]);
        }
        attempts++;
      }

      // Shuffle options
      const options = [targetWord, ...distractors].sort(() => Math.random() - 0.5);

      currentQuestion = {
        target: targetWord,
        targetMeaning: selectedMeaning,
        options: options
      };

      // Display Question
      quizQuestion.textContent = targetWord.word;

      // Add Reference Sentence (Masked)
      if (selectedMeaning.example) {
        const refDiv = document.createElement('div');
        refDiv.id = 'quiz-reference';
        refDiv.style.marginBottom = '15px';
        refDiv.style.fontStyle = 'italic';
        refDiv.style.color = '#555';
        refDiv.style.padding = '10px';
        refDiv.style.background = 'rgba(255,255,255,0.5)';
        refDiv.style.borderRadius = '8px';

        // Mask the word in the example (Escape special chars for Regex)
        const escapedWord = targetWord.word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(escapedWord, 'gi');
        const maskedExample = selectedMeaning.example.replace(regex, '______');

        refDiv.innerHTML = `<strong>Reference:</strong> "${maskedExample}"`;
        // Insert after question
        quizQuestion.parentNode.insertBefore(refDiv, quizOptions);
      }

      options.forEach(opt => {
        const btn = document.createElement('div');
        btn.className = 'option-btn';

        let defText = "No definition available";

        // For target, use the SELECTED meaning
        if (opt === targetWord) {
          defText = extractEnglish(selectedMeaning.definition);
        } else {
          // For distractors, use their most common meaning (English only)
          if (opt.analysis && opt.analysis.most_common_meaning) {
            defText = extractEnglish(opt.analysis.most_common_meaning.definition);
          }
        }

        btn.textContent = defText;
        btn.addEventListener('click', () => checkAnswer(opt, btn));
        quizOptions.appendChild(btn);
      });
    } catch (error) {
      console.error("Quiz Error:", error);
      quizFeedback.innerHTML = `<span style="color:red">Error generating question. Please try again.</span>`;
      quizFeedback.classList.add('show');
      nextQuestionBtn.style.display = 'block';
    }
  }

  function extractEnglish(text) {
    if (!text) return "";

    // Remove Chinese characters (Unicode range \u4e00-\u9fff)
    // Also remove full-width punctuation often used with Chinese
    let cleaned = text.replace(/[\u4e00-\u9fff\u3000-\u303f\uff01-\uff5e]/g, "");

    // Trim whitespace
    cleaned = cleaned.trim();

    // Remove leading/trailing punctuation/symbols that might be left over
    // e.g. ", (definition)" -> "(definition)"
    cleaned = cleaned.replace(/^[,;:\s]+/, "").replace(/[,;:\s]+$/, "");

    // If wrapped in parens, remove them
    if (cleaned.startsWith('(') && cleaned.endsWith(')')) {
      cleaned = cleaned.substring(1, cleaned.length - 1).trim();
    }

    return cleaned || text; // Fallback to text if empty (though unlikely)
  }

  function checkAnswer(selectedOption, btnElement) {
    try {
      if (nextQuestionBtn.style.display === 'block') return; // Already answered

      const isCorrect = selectedOption.word === currentQuestion.target.word;

      // Highlight selected
      if (isCorrect) {
        btnElement.classList.add('correct');
        quizScore++;
        quizScoreDisplay.textContent = `Score: ${quizScore}`;
        quizFeedback.innerHTML = '<span style="color:green">Correct!</span>';
      } else {
        btnElement.classList.add('wrong');
        // Highlight correct one
        const correctIndex = currentQuestion.options.findIndex(o => o.word === currentQuestion.target.word);
        if (correctIndex !== -1) {
          quizOptions.children[correctIndex].classList.add('correct');
        }

        const correctDef = extractEnglish(currentQuestion.targetMeaning.definition);
        quizFeedback.innerHTML = `<span style="color:red">Incorrect.</span> The correct answer is <b>${currentQuestion.target.word}</b>: ${correctDef}`;

        // Track Mistake
        trackMistake(currentQuestion.target, selectedOption);
      }

      quizFeedback.classList.add('show');
      nextQuestionBtn.style.display = 'block';

      // Scroll to bottom to ensure button is visible
      const quizContainer = document.querySelector('.question-card');
      if (quizContainer) {
        quizContainer.scrollTop = quizContainer.scrollHeight;
      }
    } catch (error) {
      console.error("Error in checkAnswer:", error);
      // Force show button so user isn't stuck
      nextQuestionBtn.style.display = 'block';
    }
  }

  function trackMistake(word, wrongChoice) {
    const mistake = {
      word: word.word,
      testedMeaning: extractEnglish(currentQuestion.targetMeaning.definition),
      wrongChoiceWord: wrongChoice.word,
      timestamp: new Date().toISOString()
    };

    mistakes.push(mistake);
    saveMistakes();
    updateDownloadBtn();
  }

  function saveMistakes() {
    localStorage.setItem('vocabulary_mistakes', JSON.stringify(mistakes));
  }

  function loadMistakes() {
    const storedMistakes = localStorage.getItem('vocabulary_mistakes');
    if (storedMistakes) {
      try {
        mistakes = JSON.parse(storedMistakes);
        updateDownloadBtn();
      } catch (e) {
        console.error("Error parsing mistakes from localStorage", e);
      }
    }
  }

  function updateDownloadBtn() {
    if (mistakes.length > 0) {
      downloadMistakesBtn.style.display = 'block';
      downloadMistakesBtn.textContent = `Download Mistakes (${mistakes.length})`;
    }
  }

  function downloadMistakes() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(mistakes, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "vocabulary_mistakes.json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }

  function resetCard() {
    if (card.classList.contains('is-flipped')) {
      card.classList.remove('is-flipped');
    }
  }

  function loadCard(index) {
    const wordData = words[index];
    currentIndexDisplay.textContent = index + 1;

    // Front
    wordDisplay.textContent = wordData.word;

    // Back
    renderAnalysis(wordData);

    // Update External Link
    const cambridgeLink = document.getElementById('cambridge-link');
    const url = `https://dictionary.cambridge.org/dictionary/english-chinese-traditional/${wordData.word}`;
    cambridgeLink.href = url;

    // Fetch and Embed Cambridge Content
    fetchCambridgeData(url);

    // Update MW Link & Fetch
    const mwLink = document.getElementById('mw-link');
    const mwUrl = `https://www.merriam-webster.com/dictionary/${wordData.word}`;
    mwLink.href = mwUrl;
    fetchMerriamWebsterData(mwUrl);
  }

  async function fetchMerriamWebsterData(url) {
    const analysisContent = document.getElementById('analysis-content');

    // Create container for MW data if not exists
    let mwContainer = document.getElementById('mw-content');
    if (!mwContainer) {
      mwContainer = document.createElement('div');
      mwContainer.id = 'mw-content';
      mwContainer.style.marginTop = '20px';
      mwContainer.style.paddingTop = '20px';
      mwContainer.style.borderTop = '2px dashed #ccc';
      analysisContent.appendChild(mwContainer);
    }

    mwContainer.innerHTML = '<p style="color:#666; font-style:italic;">Loading Merriam-Webster content...</p>';

    try {
      // Use local proxy to bypass CORS
      const proxyUrl = `/api/proxy?url=${encodeURIComponent(url)}`;
      const response = await fetch(proxyUrl);

      if (!response.ok) throw new Error('Network response was not ok');
      const text = await response.text();

      const parser = new DOMParser();
      const doc = parser.parseFromString(text, 'text/html');

      const entries = doc.querySelectorAll('div[id^="dictionary-entry-"]');

      if (entries.length > 0) {
        mwContainer.innerHTML = '<h3>Merriam-Webster Source:</h3>';
        const entry = entries[0];
        const scripts = entry.querySelectorAll('script, style, .widget, .ad, .social-share');
        scripts.forEach(el => el.remove());

        const links = entry.querySelectorAll('a');
        links.forEach(a => {
          if (a.getAttribute('href')?.startsWith('/')) {
            a.href = 'https://www.merriam-webster.com' + a.getAttribute('href');
          }
          a.target = '_blank';
          a.style.color = '#375f7d';
          a.style.textDecoration = 'underline';
        });

        mwContainer.appendChild(entry);
      } else {
        mwContainer.innerHTML = '<p>Could not extract content automatically. Please use the link below.</p>';
      }
    } catch (error) {
      console.log('MW Fetch error (expected on static host):', error);
      mwContainer.innerHTML = '<p style="color:#666; font-size: 0.9rem;">Preview not available in static mode. <br>Please click the button above to view on Merriam-Webster.</p>';
    }
  }

  async function fetchCambridgeData(url) {
    const analysisContent = document.getElementById('analysis-content');

    let cambridgeContainer = document.getElementById('cambridge-content');
    if (!cambridgeContainer) {
      cambridgeContainer = document.createElement('div');
      cambridgeContainer.id = 'cambridge-content';
      cambridgeContainer.style.marginTop = '20px';
      cambridgeContainer.style.paddingTop = '20px';
      cambridgeContainer.style.borderTop = '2px dashed #ccc';
      analysisContent.appendChild(cambridgeContainer);
    }

    cambridgeContainer.innerHTML = '<p style="color:#666; font-style:italic;">Loading Cambridge Dictionary content...</p>';

    try {
      // Use local proxy to bypass CORS
      const proxyUrl = `/api/proxy?url=${encodeURIComponent(url)}`;
      const response = await fetch(proxyUrl);

      if (!response.ok) throw new Error('Network response was not ok');
      const text = await response.text();

      const parser = new DOMParser();
      const doc = parser.parseFromString(text, 'text/html');

      const entryBody = doc.querySelector('.di-body') || doc.querySelector('.def-block');

      if (entryBody) {
        const scripts = entryBody.querySelectorAll('script, style, .runon-title, .runon-body');
        scripts.forEach(el => el.remove());

        const links = entryBody.querySelectorAll('a');
        links.forEach(a => {
          const title = a.title ? a.title.toLowerCase() : '';
          const isIdiom = title.endsWith('idiom') ||
            title.endsWith('phrasal verb') ||
            title.startsWith('meaning of') ||
            a.querySelector('.idiom');

          if (isIdiom) {
            if (a.getAttribute('href')?.startsWith('/')) {
              a.href = 'https://dictionary.cambridge.org' + a.getAttribute('href');
            }
            a.target = '_blank';
            a.style.textDecoration = 'underline';
            a.style.color = '#1d4ed8';
          } else {
            const span = document.createElement('span');
            span.innerHTML = a.innerHTML;
            span.className = 'stripped-link';
            a.replaceWith(span);
          }
        });

        cambridgeContainer.innerHTML = '<h3>Cambridge Dictionary Source:</h3>';
        cambridgeContainer.appendChild(entryBody);
      } else {
        cambridgeContainer.innerHTML = '<p>Could not extract content automatically. Please use the link below.</p>';
      }
    } catch (error) {
      console.log('Fetch error (expected on static host):', error);
      cambridgeContainer.innerHTML = '<p style="color:#666; font-size: 0.9rem;">Preview not available in static mode. <br>Please click the button above to view on Cambridge Dictionary.</p>';
    }
  }

  function renderAnalysis(data) {
    analysisContent.innerHTML = '';

    if (!data.analysis) {
      analysisContent.innerHTML = '<p style="text-align:center; margin-top: 20px;">No detailed analysis available for this word.</p>';
      return;
    }

    const { most_common_meaning, less_common_meanings, word_family, related_phrases } = data.analysis;

    // 1. 主要意思 (Most Common Meaning)
    if (most_common_meaning) {
      const section = createSection('1. 主要意思 (Most Common Meaning)');
      section.appendChild(createDetailItem('詞性', most_common_meaning.part_of_speech));
      section.appendChild(createDetailItem('定義', most_common_meaning.definition));
      section.appendChild(createDetailItem('例句', most_common_meaning.example));
      analysisContent.appendChild(section);
    }

    // 2. 次要/不常見意思 (Less Common Meanings)
    if (less_common_meanings && less_common_meanings.length > 0) {
      const section = createSection('2. 次要/不常見意思 (Less Common Meanings)');
      const ul = document.createElement('ul');
      ul.style.paddingLeft = '20px';

      less_common_meanings.forEach(item => {
        const li = document.createElement('li');
        li.style.marginBottom = '10px';
        li.appendChild(createDetailItem('詞性', item.part_of_speech));
        li.appendChild(createDetailItem('定義', item.definition));
        li.appendChild(createDetailItem('例句', item.example));
        ul.appendChild(li);
      });
      section.appendChild(ul);
      analysisContent.appendChild(section);
    }

    // 3. 相關衍生字 (Word Family)
    if (word_family && word_family.length > 0) {
      const section = createSection('3. 相關衍生字 (Word Family)');
      const ul = document.createElement('ul');
      ul.style.paddingLeft = '20px';

      word_family.forEach(item => {
        const li = document.createElement('li');
        li.textContent = `${item.word} (${item.part_of_speech}): ${item.definition}`;
        ul.appendChild(li);
      });
      section.appendChild(ul);
      analysisContent.appendChild(section);
    }

    // 4. 相關片語/慣用語 (Related Phrases/Idioms)
    if (related_phrases && related_phrases.length > 0) {
      const section = createSection('4. 相關片語/慣用語 (Related Phrases/Idioms)');
      const ul = document.createElement('ul');
      ul.style.paddingLeft = '20px';

      related_phrases.forEach(item => {
        const li = document.createElement('li');
        li.style.marginBottom = '10px';
        li.appendChild(createDetailItem('片語', item.phrase));
        li.appendChild(createDetailItem('定義', item.definition));
        li.appendChild(createDetailItem('例句', item.example));
        ul.appendChild(li);
      });
      section.appendChild(ul);
      analysisContent.appendChild(section);
    }
  }

  function createSection(title) {
    const div = document.createElement('div');
    div.style.marginBottom = '20px';
    const h3 = document.createElement('h3');
    h3.className = 'section-title';
    h3.textContent = title;
    div.appendChild(h3);
    return div;
  }

  function createDetailItem(label, content) {
    const div = document.createElement('div');
    div.className = 'definition-item';
    if (!content) content = '(None)';
    div.innerHTML = `<strong>${label}:</strong> ${content}`;
    return div;
  }


  // --- Highlight to Search Feature ---
  const searchTooltip = document.getElementById('search-tooltip');
  const searchBtn = document.getElementById('search-cambridge-btn');
  let selectedText = '';

  document.addEventListener('mouseup', (e) => {
    // Wait a bit for selection to complete
    setTimeout(() => {
      const selection = window.getSelection();
      const text = selection.toString().trim();

      if (text.length > 0) {
        // Check if we are inside the card container (optional restriction)
        // For now, allow anywhere on the page

        selectedText = text;

        // Position tooltip near the mouse/selection
        // We can use the bounding rect of the selection or just the mouse coordinates
        // Using mouse coordinates from the event is easier for 'mouseup'

        // But 'mouseup' event might happen on the button itself, so handle that
        if (e.target === searchBtn) return;

        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Calculate position (centered above selection)
        const top = rect.top + window.scrollY - 40; // 40px above
        const left = rect.left + window.scrollX + (rect.width / 2) - (searchTooltip.offsetWidth / 2);

        searchTooltip.style.top = `${top}px`;
        searchTooltip.style.left = `${left}px`;
        searchTooltip.style.display = 'block';
      } else {
        searchTooltip.style.display = 'none';
      }
    }, 10);
  });

  // Hide tooltip when clicking elsewhere (mousedown clears selection usually, but let's be safe)
  document.addEventListener('mousedown', (e) => {
    if (e.target !== searchBtn && !searchTooltip.contains(e.target)) {
      searchTooltip.style.display = 'none';
    }
  });

  searchBtn.addEventListener('click', () => {
    if (selectedText) {
      const url = `https://dictionary.cambridge.org/dictionary/english-chinese-traditional/${encodeURIComponent(selectedText)}`;
      window.open(url, '_blank');
      searchTooltip.style.display = 'none';
      // Optional: Clear selection
      window.getSelection().removeAllRanges();
    }
  });

});
