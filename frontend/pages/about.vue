<template>
  <div class="flex flex-col min-h-screen py-12">
    <div class="container mx-auto px-4 max-w-5xl">
      <h1 class="text-3xl font-bold mb-8 text-center">About Toolhunt</h1>

      <div class="card bg-base-100 shadow-xl">
        <div class="bg-secondary text-secondary-content p-4 pl-10 rounded-t-xl">
          <h2 class="text-2xl font-bold">Welcome to Toolhunt!</h2>
        </div>
        <div class="card-body pt-6">
          <div class="prose prose-lg max-w-none text-base-content">
            <p>
              Toolhunt is a simple web app for editing
              <a href="https://toolhub.wikimedia.org" target="_blank" rel="noopener noreferrer" class="link">Toolhub</a>
              records. It helps you find tools with missing information and add that information in a straightforward way.
            </p>

            <h3 class="text-2xl font-semibold mt-8 mb-4 text-secondary">What's Toolhub?</h3>
            <p>
              <a href="https://toolhub.wikimedia.org" target="_blank" rel="noopener noreferrer" class="link">Toolhub</a>
              is a catalog of tools used in various Wiki projects. It's meant to help
              people find and use tools for their Wiki work. The more complete the information
              in Toolhub, the more useful it is for everyone.
            </p>

            <h3 class="text-2xl font-semibold mt-8 mb-4 text-secondary">How Toolhunt Works</h3>
            <ul class="list-disc pl-6 space-y-2">
              <li>We show you tools from Toolhub that are missing some information.</li>
              <li>You can add the missing details if you know them.</li>
              <li>That's pretty much it!</li>
            </ul>

            <h3 class="text-2xl font-semibold mt-8 mb-4 text-secondary">Where Toolhunt Came From</h3>
            <p>
              Toolhunt started as an
              <a href="https://www.outreachy.org/" target="_blank" rel="noopener noreferrer" class="link">Outreachy</a>
              internship project. It was inspired by
              <a href="https://citationhunt.toolforge.org/" target="_blank" rel="noopener noreferrer" class="link">Citation Hunt</a>,
              which helps people add missing citations on Wikipedia. We thought something similar
              could work for Toolhub.
            </p>

            <h3 class="text-2xl font-semibold mt-8 mb-4 text-secondary">Want to Help?</h3>
            <p>
              If you know about Wiki tools and want to improve Toolhub's information, give Toolhunt a try.
              Even small contributions can be helpful.
            </p>

            <div class="mt-8 flex justify-center">
              <NuxtLink to="/" class="btn btn-accent">Let's go!</NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
