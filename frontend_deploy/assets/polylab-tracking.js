(function () {
  if (window.PolyLabTracking && typeof window.PolyLabTracking.init === "function") {
    return;
  }

  var config = Object.freeze({
    supabaseUrl: "https://wdwvmsrqepxvhkmodqks.supabase.co",
    supabaseAnonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indkd3Ztc3JxZXB4dmhrbW9kcWtzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYxNDk1MjgsImV4cCI6MjA4MTcyNTUyOH0.f91s-hoa31u5LY29Xt-rTbt8n9sdOvPOzBW6R3IsC00",
    table: "marketing_events",
    sessionStorageKey: "polylab_tracking_session_id",
    firstTouchStorageKey: "polylab_tracking_first_touch",
    initializedKey: "polylab_tracking_initialized",
    sdkSrc: "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"
  });

  window.POLYLAB_TRACKING_CONFIG = config;

  function safeStorageGet(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (_) {
      return null;
    }
  }

  function safeStorageSet(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_) {
      // ignore storage failures
    }
  }

  function safeJsonParse(value) {
    if (!value) {
      return null;
    }

    try {
      return JSON.parse(value);
    } catch (_) {
      return null;
    }
  }

  function buildFallbackId() {
    return "sess_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 10);
  }

  function getSessionId() {
    var existing = safeStorageGet(config.sessionStorageKey);
    if (existing) {
      return existing;
    }

    var nextId = window.crypto && typeof window.crypto.randomUUID === "function"
      ? window.crypto.randomUUID()
      : buildFallbackId();
    safeStorageSet(config.sessionStorageKey, nextId);
    return nextId;
  }

  function getPageKey() {
    return document.body && document.body.getAttribute("data-page-key")
      ? document.body.getAttribute("data-page-key")
      : "unknown";
  }

  function getLandingVariant() {
    return document.body && document.body.getAttribute("data-landing-variant")
      ? document.body.getAttribute("data-landing-variant")
      : null;
  }

  function getUtmValue(searchParams, key) {
    var value = searchParams.get(key);
    return value && value.length ? value : null;
  }

  function getCurrentContextPayload() {
    var params = new URLSearchParams(window.location.search || "");
    return {
      session_id: getSessionId(),
      page_path: window.location.pathname + window.location.search,
      page_key: getPageKey(),
      landing_variant: getLandingVariant(),
      referrer: document.referrer || null,
      utm_source: getUtmValue(params, "utm_source"),
      utm_medium: getUtmValue(params, "utm_medium"),
      utm_campaign: getUtmValue(params, "utm_campaign"),
      utm_term: getUtmValue(params, "utm_term"),
      utm_content: getUtmValue(params, "utm_content")
    };
  }

  function getStoredFirstTouch() {
    return safeJsonParse(safeStorageGet(config.firstTouchStorageKey)) || {};
  }

  function persistFirstTouch(context) {
    var existing = getStoredFirstTouch();
    if (existing && existing.entry_page_path) {
      return existing;
    }

    var firstTouch = {
      utm_source: context.utm_source,
      utm_medium: context.utm_medium,
      utm_campaign: context.utm_campaign,
      utm_term: context.utm_term,
      utm_content: context.utm_content,
      referrer: context.referrer,
      entry_page_path: context.page_path,
      entry_landing_variant: context.landing_variant
    };
    safeStorageSet(config.firstTouchStorageKey, JSON.stringify(firstTouch));
    return firstTouch;
  }

  function getContextPayload() {
    var current = getCurrentContextPayload();
    var stored = persistFirstTouch(current);

    return {
      session_id: current.session_id,
      page_path: current.page_path,
      page_key: current.page_key,
      landing_variant: current.landing_variant,
      referrer: current.referrer || stored.referrer || null,
      utm_source: current.utm_source || stored.utm_source || null,
      utm_medium: current.utm_medium || stored.utm_medium || null,
      utm_campaign: current.utm_campaign || stored.utm_campaign || null,
      utm_term: current.utm_term || stored.utm_term || null,
      utm_content: current.utm_content || stored.utm_content || null,
      entry_page_path: stored.entry_page_path || current.page_path,
      entry_landing_variant: stored.entry_landing_variant || current.landing_variant || null
    };
  }

  var supabaseClientPromise = null;

  function loadSupabaseSdk() {
    if (window.supabase && typeof window.supabase.createClient === "function") {
      return Promise.resolve(window.supabase);
    }

    if (supabaseClientPromise) {
      return supabaseClientPromise;
    }

    supabaseClientPromise = new Promise(function (resolve, reject) {
      var existing = document.querySelector('script[data-polylab-supabase-sdk="true"]');
      if (existing) {
        existing.addEventListener("load", function () {
          if (window.supabase && typeof window.supabase.createClient === "function") {
            resolve(window.supabase);
          } else {
            reject(new Error("Supabase SDK unavailable after load"));
          }
        }, { once: true });
        existing.addEventListener("error", function () {
          reject(new Error("Supabase SDK failed to load"));
        }, { once: true });
        return;
      }

      var script = document.createElement("script");
      script.src = config.sdkSrc;
      script.async = true;
      script.setAttribute("data-polylab-supabase-sdk", "true");
      script.onload = function () {
        if (window.supabase && typeof window.supabase.createClient === "function") {
          resolve(window.supabase);
        } else {
          reject(new Error("Supabase SDK unavailable after load"));
        }
      };
      script.onerror = function () {
        reject(new Error("Supabase SDK failed to load"));
      };
      document.head.appendChild(script);
    });

    return supabaseClientPromise;
  }

  function getClient() {
    return loadSupabaseSdk().then(function (sdk) {
      if (!window.__polylabTrackingSupabaseClient) {
        window.__polylabTrackingSupabaseClient = sdk.createClient(config.supabaseUrl, config.supabaseAnonKey, {
          auth: {
            autoRefreshToken: false,
            persistSession: true,
            detectSessionInUrl: true
          }
        });
      }

      return window.__polylabTrackingSupabaseClient;
    });
  }

  function getCurrentUser(client) {
    return client.auth.getSession().then(function (result) {
      return result && result.data && result.data.session && result.data.session.user
        ? result.data.session.user
        : null;
    }).catch(function () {
      return null;
    });
  }

  function elementText(element) {
    if (!element) {
      return null;
    }

    var label = element.getAttribute("data-track-label");
    if (label && label.length) {
      return label;
    }

    var text = element.textContent || "";
    text = text.replace(/\s+/g, " ").trim();
    return text.length ? text : null;
  }

  function normalizeMetadata(metadata, element) {
    var result = {};
    var key;

    if (metadata && typeof metadata === "object") {
      for (key in metadata) {
        if (Object.prototype.hasOwnProperty.call(metadata, key) && metadata[key] != null) {
          result[key] = metadata[key];
        }
      }
    }

    if (element) {
      if (element.getAttribute("href")) {
        result.href = element.getAttribute("href");
      }
      if (elementText(element)) {
        result.label = elementText(element);
      }
      if (element.getAttribute("data-track-placement")) {
        result.placement = element.getAttribute("data-track-placement");
      }
    }

    return result;
  }

  function track(eventName, metadata, element) {
    return getClient().then(function (client) {
      return getCurrentUser(client).then(function (user) {
        var context = getContextPayload();
        return client
          .from(config.table)
          .insert({
            event_name: eventName,
            user_id: user ? user.id : null,
            session_id: context.session_id,
            page_path: context.page_path,
            page_key: context.page_key,
            landing_variant: context.landing_variant,
            referrer: context.referrer,
            utm_source: context.utm_source,
            utm_medium: context.utm_medium,
            utm_campaign: context.utm_campaign,
            utm_term: context.utm_term,
            utm_content: context.utm_content,
            metadata: normalizeMetadata(Object.assign({
              entry_page_path: context.entry_page_path,
              entry_landing_variant: context.entry_landing_variant
            }, metadata || {}), element)
          });
      });
    }).catch(function (error) {
      if (window.console && typeof window.console.warn === "function") {
        console.warn("PolyLab tracking skipped:", error && error.message ? error.message : error);
      }
      return null;
    });
  }

  function bindClickTracking() {
    document.addEventListener("click", function (event) {
      var target = event.target && typeof event.target.closest === "function"
        ? event.target.closest("[data-track-event]")
        : null;

      if (!target) {
        return;
      }

      track(target.getAttribute("data-track-event") || "cta_click", {
        target_page_key: target.getAttribute("data-track-target") || null
      }, target);
    });
  }

  function init() {
    if (document.body && document.body.getAttribute(config.initializedKey) === "true") {
      return;
    }

    if (document.body) {
      document.body.setAttribute(config.initializedKey, "true");
    }

    bindClickTracking();
    track("page_view", {
      title: document.title
    });
  }

  window.PolyLabTracking = {
    init: init,
    track: track
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
}());
