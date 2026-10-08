/**
 * Jest setup file - runs before all tests
 * Mocks jQuery and browser APIs needed by common.js
 */

// Mock jQuery
global.$ = function(selector) {
  const element = {
    addClass: jest.fn().mockReturnThis(),
    removeClass: jest.fn().mockReturnThis(),
    toggleClass: jest.fn().mockReturnThis(),
    hasClass: jest.fn().mockReturnValue(false),
    show: jest.fn().mockReturnThis(),
    hide: jest.fn().mockReturnThis(),
    toggle: jest.fn().mockReturnThis(),
    text: jest.fn().mockReturnThis(),
    html: jest.fn().mockReturnThis(),
    val: jest.fn().mockReturnValue(''),
    attr: jest.fn().mockReturnThis(),
    prop: jest.fn().mockReturnValue({}),
    append: jest.fn().mockReturnThis(),
    prepend: jest.fn().mockReturnThis(),
    remove: jest.fn().mockReturnThis(),
    empty: jest.fn().mockReturnThis(),
    focus: jest.fn().mockReturnThis(),
    click: jest.fn().mockReturnThis(),
    each: jest.fn(),
    children: jest.fn().mockReturnValue([]),
    parent: jest.fn().mockReturnThis(),
    is: jest.fn().mockReturnValue(false),
    length: 0,
    data: jest.fn().mockReturnValue(undefined),
    css: jest.fn().mockReturnThis(),
    after: jest.fn().mockReturnThis(),
    before: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    off: jest.fn().mockReturnThis(),
    submit: jest.fn().mockReturnThis(),
    keydown: jest.fn().mockReturnThis(),
    load: jest.fn().mockReturnThis(),
    modal: jest.fn().mockReturnThis(),
    ready: jest.fn(function(callback) {
      // Don't execute the callback during testing to avoid side effects
      return this;
    }),
  };
  return element;
};

// jQuery static methods
global.$.fn = {
  serializeArray: jest.fn().mockReturnValue([]),
  serializeObject: jest.fn().mockReturnValue({}),
};

global.$.each = jest.fn((arr, callback) => {
  if (Array.isArray(arr)) {
    arr.forEach(callback);
  }
});

global.$.ajax = jest.fn().mockReturnValue({
  done: jest.fn().mockReturnThis(),
  fail: jest.fn().mockReturnThis(),
  always: jest.fn().mockReturnThis(),
});

global.$.notify = jest.fn();
global.$.param = jest.fn((obj) => 'mocked=params');

// Mock browser APIs
global.window = {
  location: {
    search: '?cid=1',
    pathname: '/test',
    href: 'http://localhost/test?cid=1',
  },
};

global.document = {
  cookie: '',
  body: {
    appendChild: jest.fn(),
  },
  createElement: jest.fn(() => ({
    setAttribute: jest.fn(),
    click: jest.fn(),
    remove: jest.fn(),
  })),
  getElementById: jest.fn(),
  querySelector: jest.fn(),
};

// Mock DOMParser
global.DOMParser = class {
  parseFromString(str, type) {
    return {
      body: {
        childNodes: str.includes('<') ? [{ nodeType: 1 }] : [],
      },
      documentElement: {
        textContent: str.replace(/<[^>]*>/g, ''),
      },
    };
  }
};

// Mock URLSearchParams
global.URLSearchParams = class {
  constructor(search) {
    this.params = {};
    if (search) {
      search.replace(/^\?/, '').split('&').forEach(pair => {
        const [key, value] = pair.split('=');
        if (key) this.params[key] = value || '';
      });
    }
  }
  get(key) {
    return this.params[key] || null;
  }
  delete(key) {
    delete this.params[key];
  }
  toString() {
    return Object.entries(this.params).map(([k, v]) => `${k}=${v}`).join('&');
  }
};

// Mock atob/btoa for base64
global.atob = (str) => Buffer.from(str, 'base64').toString('binary');
global.btoa = (str) => Buffer.from(str, 'binary').toString('base64');

// Mock Date for consistent testing (optional, only if needed)
// Uncomment if tests need consistent dates
// const realDate = Date;
// global.Date = class extends realDate {
//   constructor(...args) {
//     if (args.length === 0) {
//       return new realDate('2024-06-09T12:00:00Z');
//     }
//     return new realDate(...args);
//   }
// };
