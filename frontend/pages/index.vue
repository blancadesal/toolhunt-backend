<script setup>
import { ref, onMounted, computed } from 'vue';
const { authState } = useAuth();

const tasks = ref([]);
const currentTaskIndex = ref(0);
const userInput = ref('');
const searchQuery = ref('');

const isLoggedIn = computed(() => authState.value?.user != null);
const currentTask = computed(() => tasks.value[currentTaskIndex.value] || null);

const fetchTasks = async () => {
  // Replace this with an actual API call
  tasks.value = [
    {
        "field": {
            "description": "With what type of content or data does the tool interact?",
            "input_options": {
                "article": "Articles",
                "audio": "Audio",
                "book": "Books",
                "data::bibliography": "Bibliographic data",
                "data::category": "Categories or labels",
                "data::diff": "Diffs and revision data",
                "data::event": "Event data",
                "data::geography": "Geographic data",
                "data::linguistic": "Linguistic data",
                "data::page_metadata": "Page metadata",
                "data::structured": "Structured data",
                "data::user": "User data",
                "discussion": "Discussions",
                "draft": "Drafts",
                "email": "Emails",
                "image": "Images",
                "link": "Links",
                "list": "Lists",
                "log": "Logs",
                "map": "Maps",
                "reference": "References",
                "software": "Software or code",
                "template": "Templates",
                "video": "Videos",
                "watchlist": "Watchlists",
                "webpage": "Webpages",
                "wikitext": "Wikitext"
            },
            "name": "content_types",
            "pattern": null
        },
        "id": 1758069,
        "tool": {
            "description": "See [[:en:User:PrimeBOT]]",
            "name": "toolforge-primebot",
            "title": "A bot used by Primefac on the English Wikipedia ",
            "url": "https://toolsadmin.wikimedia.org/tools/id/primebot"
        }
    },
    {
        "field": {
            "description": "With what type of content or data does the tool interact?",
            "input_options": {
                "article": "Articles",
                "audio": "Audio",
                "book": "Books",
                "data::bibliography": "Bibliographic data",
                "data::category": "Categories or labels",
                "data::diff": "Diffs and revision data",
                "data::event": "Event data",
                "data::geography": "Geographic data",
                "data::linguistic": "Linguistic data",
                "data::page_metadata": "Page metadata",
                "data::structured": "Structured data",
                "data::user": "User data",
                "discussion": "Discussions",
                "draft": "Drafts",
                "email": "Emails",
                "image": "Images",
                "link": "Links",
                "list": "Lists",
                "log": "Logs",
                "map": "Maps",
                "reference": "References",
                "software": "Software or code",
                "template": "Templates",
                "video": "Videos",
                "watchlist": "Watchlists",
                "webpage": "Webpages",
                "wikitext": "Wikitext"
            },
            "name": "content_types",
            "pattern": null
        },
        "id": 1696867,
        "tool": {
            "description": "Hold your queries here!",
            "name": "toolforge-query-chest",
            "title": "Query Chest",
            "url": "https://query-chest.toolforge.org/"
        }
    },
    {
        "field": {
            "description": "The manner in which the tool is used. Select one from the list of options.",
            "input_options": {
                "bot": "Bot",
                "coding framework": "Coding framework",
                "command line tool": "Command line tool",
                "desktop app": "Desktop app",
                "gadget": "Gadget",
                "lua module": "LUA module",
                "other": "Other",
                "template": "Template",
                "user script": "User script",
                "web app": "Web app"
            },
            "name": "tool_type",
            "pattern": null
        },
        "id": 1756831,
        "tool": {
            "description": "Tool to help with the classification of Wikidata items which do not have any classification statement.",
            "name": "toolforge-classifywd",
            "title": "Wikidata Classify",
            "url": "https://toolsadmin.wikimedia.org/tools/id/classifywd"
        }
    },
    {
        "field": {
            "description": "Wikidata item ID for the tool.",
            "input_options": null,
            "name": "wikidata_qid",
            "pattern": "^Q\\d+$"
        },
        "id": 1703336,
        "tool": {
            "description": "Test deployment for Proyecto Chaco",
            "name": "toolforge-chaco-test",
            "title": "Test for Proyecto Chaco",
            "url": "https://chaco-test.toolforge.org/"
        }
    },
    {
        "field": {
            "description": "The manner in which the tool is used. Select one from the list of options.",
            "input_options": {
                "bot": "Bot",
                "coding framework": "Coding framework",
                "command line tool": "Command line tool",
                "desktop app": "Desktop app",
                "gadget": "Gadget",
                "lua module": "LUA module",
                "other": "Other",
                "template": "Template",
                "user script": "User script",
                "web app": "Web app"
            },
            "name": "tool_type",
            "pattern": null
        },
        "id": 1801859,
        "tool": {
            "description": "https://en.wikipedia.org/wiki/User:RichBot",
            "name": "toolforge-richbot",
            "title": "RichBot",
            "url": "https://toolsadmin.wikimedia.org/tools/id/richbot"
        }
    },
    {
        "field": {
            "description": "Is the tool targeted at helping in a specific type of wiki project or topic area?",
            "input_options": {
                "biography": "Biography",
                "cultural": "Cultural heritage",
                "education": "Education",
                "geography": "Geography and mapping",
                "glam": "GLAM",
                "history": "History",
                "language": "Language and internationalization",
                "outreach": "Outreach",
                "science": "Science"
            },
            "name": "subject_domains",
            "pattern": null
        },
        "id": 1760183,
        "tool": {
            "description": "Tool to help add main subjects to items",
            "name": "toolforge-itemsubjector",
            "title": "ItemSubjector",
            "url": "https://www.wikidata.org/wiki/Q115100941"
        }
    },
    {
        "field": {
            "description": "A link to the tool's translation interface.",
            "input_options": null,
            "name": "translate_url",
            "pattern": null
        },
        "id": 1797787,
        "tool": {
            "description": "Adds a link to the [[WP:GOCE|Guild of Copy Editors]] to the \"Navigation\" menu. Check the docs for other options.",
            "name": "enwiki-ritenerek-goce",
            "title": "GOCE",
            "url": "https://en.wikipedia.org/wiki/User:Ritenerek/js/goce_nav.js"
        }
    },
    {
        "field": {
            "description": "A link to a Wikimedia Commons file description page for an icon that depicts the tool.",
            "input_options": null,
            "name": "icon",
            "pattern": "^https://commons\\.wikimedia\\.org/wiki/File:.+\\..+$"
        },
        "id": 1779359,
        "tool": {
            "description": "A site to show the top 25 most visited Wikipedia articles for a timespan.",
            "name": "toolforge-top25report-site",
            "title": "Top25Report Site",
            "url": "https://top25report-site.toolforge.org/"
        }
    },
    {
        "field": {
            "description": "Who is the intended user of the tool?",
            "input_options": {
                "admin": "Admins",
                "developer": "Developers",
                "editor": "Editors and content contributors",
                "organizer": "Organizers and program coordinators",
                "reader": "Readers and content consumers",
                "researcher": "Researchers"
            },
            "name": "audiences",
            "pattern": null
        },
        "id": 1742265,
        "tool": {
            "description": "Random good or excellent article on several Wikipedias",
            "name": "random-featured",
            "title": "random-featured",
            "url": "https://random-featured.toolforge.org/"
        }
    },
    {
        "field": {
            "description": "Wikidata item ID for the tool.",
            "input_options": null,
            "name": "wikidata_qid",
            "pattern": "^Q\\d+$"
        },
        "id": 1650210,
        "tool": {
            "description": "Sandbox for bd808 to play with ruby things",
            "name": "toolforge-bd808-ruby",
            "title": "bd808's ruby sandbox",
            "url": "https://toolsadmin.wikimedia.org/tools/id/bd808-ruby"
        }
    }
];
  shuffleTasks();
};

const shuffleTasks = () => {
  for (let i = tasks.value.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [tasks.value[i], tasks.value[j]] = [tasks.value[j], tasks.value[i]];
  }
};

const nextTask = () => {
  currentTaskIndex.value = (currentTaskIndex.value + 1) % tasks.value.length;
  userInput.value = '';
};

const previousTask = () => {
  currentTaskIndex.value = (currentTaskIndex.value - 1 + tasks.value.length) % tasks.value.length;
  userInput.value = '';
};

const submitContribution = async () => {
  if (!isLoggedIn.value) {
    // Redirect to login
    return;
  }

  if (!validateInput()) {
    // Show error message
    return;
  }

  // Submit contribution logic here
  console.log(`Submitting ${userInput.value} for ${currentTask.value.tool.name}'s ${currentTask.value.field.name}`);
  nextTask();
};

const validateInput = () => {
  const field = currentTask.value.field;
  if (field.input_options) {
    return field.input_options.hasOwnProperty(userInput.value);
  } else if (field.pattern) {
    return new RegExp(field.pattern).test(userInput.value);
  }
  return true; // No validation required
};

const searchTools = () => {
  // Implement search functionality
};

onMounted(fetchTasks);
</script>

<template>
  <div class="min-h-screen bg-base-200 flex flex-col items-center p-4">
    <h1 class="text-4xl font-bold mt-4 mb-4">Toolhunt</h1>

    <div class="w-full max-w-lg mb-4">
      <div class="form-control">
        <div class="relative">
          <input v-model="searchQuery" type="text" placeholder="Search for tools..." class="input input-bordered w-full pr-10" />
          <button @click="searchTools" class="absolute right-2 top-1/2 transform -translate-y-1/2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="currentTask" class="card bg-base-100 shadow-xl w-full max-w-lg">
      <div class="card-body">
        <h2 class="card-title text-2xl mb-2">{{ currentTask.tool.title }}</h2>
        <p class="mb-4 text-gray-600">{{ currentTask.tool.description }}</p>
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          <a :href="currentTask.tool.url" target="_blank" class="text-blue-500 hover:underline">{{ currentTask.tool.url }}</a>
        </div>
        <div class="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4">
          <p class="font-bold">Missing Information:</p>
          <p>{{ currentTask.field.name }}</p>
          <p class="text-sm mt-2">{{ currentTask.field.description }}</p>
        </div>

        <div class="form-control">
          <label class="label">
            <span class="label-text">Help complete this tool's information:</span>
          </label>
          <div v-if="currentTask.field.input_options">
            <select v-model="userInput" class="select select-bordered w-full">
              <option disabled value="">Select an option</option>
              <option v-for="(label, value) in currentTask.field.input_options" :key="value" :value="value">
                {{ label }}
              </option>
            </select>
          </div>
          <input v-else v-model="userInput" type="text" :placeholder="`Enter ${currentTask.field.name}`" class="input input-bordered w-full" />
        </div>

        <div class="card-actions justify-between mt-4">
          <button @click="previousTask" class="btn btn-outline">Previous</button>
          <div>
            <button @click="submitContribution" class="btn btn-primary mr-2" :disabled="!isLoggedIn">
              {{ isLoggedIn ? 'Submit' : 'Login to Submit' }}
            </button>
            <button @click="nextTask" class="btn btn-ghost">Skip</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
