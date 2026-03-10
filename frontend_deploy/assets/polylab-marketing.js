(function () {
  function getContent() {
    return window.POLYLAB_INFO_CONTENT || {
      contact: { email: "hello@polylab.app" },
      contactEmail: "hello@polylab.app",
      faq: [],
      terms: [],
      privacy: []
    };
  }

  function getContactEmail(content) {
    if (content.contact && content.contact.email) {
      return content.contact.email;
    }
    return content.contactEmail || "hello@polylab.app";
  }

  function getNestedValue(source, path) {
    if (!path) {
      return undefined;
    }

    var parts = path.split(".");
    var value = source;

    for (var i = 0; i < parts.length; i += 1) {
      if (value == null || typeof value !== "object" || !(parts[i] in value)) {
        return undefined;
      }
      value = value[parts[i]];
    }

    return value;
  }

  function renderFaq(container, items) {
    if (!container) {
      return;
    }

    container.replaceChildren();

    for (var i = 0; i < items.length; i += 1) {
      var details = document.createElement("details");
      details.className = "reveal";

      var summary = document.createElement("summary");
      summary.className = "faq-question";
      summary.textContent = items[i].question;

      var answer = document.createElement("div");
      answer.className = "faq-answer";
      answer.textContent = items[i].answer;

      details.appendChild(summary);
      details.appendChild(answer);
      container.appendChild(details);
    }
  }

  function renderCopyList(container, items) {
    if (!container) {
      return;
    }

    container.replaceChildren();

    for (var i = 0; i < items.length; i += 1) {
      var item = document.createElement(container.tagName === "UL" || container.tagName === "OL" ? "li" : "div");
      item.textContent = items[i];
      container.appendChild(item);
    }
  }

  function applyCopyBindings(content) {
    var nodes = document.querySelectorAll("[data-copy-key]");

    for (var i = 0; i < nodes.length; i += 1) {
      var key = nodes[i].getAttribute("data-copy-key");
      var attr = nodes[i].getAttribute("data-copy-attr");
      var value = getNestedValue(content, key);

      if (typeof value !== "string" || value.length === 0) {
        continue;
      }

      if (attr) {
        nodes[i].setAttribute(attr, value);
      } else {
        nodes[i].textContent = value;
      }
    }
  }

  function buildModalItem(text, index) {
    var item = document.createElement("div");
    item.className = "info-modal-item";

    var badge = document.createElement("div");
    badge.className = "info-modal-index";
    badge.textContent = String(index + 1);

    var copy = document.createElement("p");
    copy.textContent = text;

    item.appendChild(badge);
    item.appendChild(copy);
    return item;
  }

  function initInfoModal(content) {
    var modal = document.querySelector("[data-info-modal]");
    if (!modal) {
      return;
    }

    var title = modal.querySelector("[data-info-modal-title]");
    var body = modal.querySelector("[data-info-modal-body]");
    var triggers = document.querySelectorAll("[data-info-trigger]");
    var closeButtons = modal.querySelectorAll("[data-info-close]");

    function closeModal() {
      modal.hidden = true;
      document.body.classList.remove("info-modal-open");
    }

    function openModal(type) {
      var items = type === "privacy" ? (content.privacy || []) : (content.terms || []);
      var heading = type === "privacy" ? "Privacy" : "Terms";

      if (title) {
        title.textContent = heading;
      }

      if (body) {
        body.replaceChildren();
        for (var i = 0; i < items.length; i += 1) {
          body.appendChild(buildModalItem(items[i], i));
        }
      }

      modal.hidden = false;
      document.body.classList.add("info-modal-open");
    }

    for (var i = 0; i < triggers.length; i += 1) {
      triggers[i].addEventListener("click", function (event) {
        event.preventDefault();
        openModal(event.currentTarget.getAttribute("data-info-trigger"));
      });
    }

    for (var j = 0; j < closeButtons.length; j += 1) {
      closeButtons[j].addEventListener("click", closeModal);
    }

    modal.addEventListener("click", function (event) {
      if (event.target === modal) {
        closeModal();
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !modal.hidden) {
        closeModal();
      }
    });
  }

  function applyContactLinks(email) {
    var links = document.querySelectorAll("[data-contact-link]");
    for (var i = 0; i < links.length; i += 1) {
      links[i].setAttribute("href", "mailto:" + email);
    }
  }

  window.initPolyLabMarketingPage = function initPolyLabMarketingPage() {
    var content = getContent();
    applyCopyBindings(content);

    var faqContainers = document.querySelectorAll("[data-faq-list]");
    for (var i = 0; i < faqContainers.length; i += 1) {
      var faqSource = faqContainers[i].getAttribute("data-faq-source");
      var faqItems = faqSource ? getNestedValue(content, faqSource) : content.faq;
      renderFaq(faqContainers[i], faqItems || []);
    }

    var listContainers = document.querySelectorAll("[data-copy-list]");
    for (var j = 0; j < listContainers.length; j += 1) {
      var listSource = listContainers[j].getAttribute("data-copy-list");
      var items = getNestedValue(content, listSource);
      renderCopyList(listContainers[j], Array.isArray(items) ? items : []);
    }

    applyContactLinks(getContactEmail(content));
    initInfoModal(content);
  };
}());
