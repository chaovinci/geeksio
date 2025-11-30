Heading
=======

Sub-heading
-----------

# Alternative heading

## Alternative sub-heading

Paragraphs are separated 
by a blank line.

Two spaces at the end of a line  
produce a line break.

Text attributes _italic_, **bold**, `monospace`.

Horizontal rule:

---

Bullet lists nested within numbered list:

  1. fruits
     * apple
     * banana
  2. vegetables
     - carrot
     - broccoli



[![Node.js CI](https://github.com/tryfabric/martian/actions/workflows/ci.yml/badge.svg)](https://github.com/tryfabric/martian/actions/workflows/ci.yml)
[![Code Style: Google](https://img.shields.io/badge/code%20style-google-blueviolet.svg)](https://github.com/google/gts)

hello _world_ 
*** 
## heading2
* [x] todo

> 📘 **Note:** Important _information_

> Some other blockquote

> This is a regular blockquote
> It can span multiple lines

> [!NOTE]
> Important information that users should know

> [!WARNING]
> Critical information that needs attention

> 📘 **Note:** This is a callout with a blue background
> It supports all markdown formatting and can span multiple lines

> ❗ **Warning:** This is a callout with a red background
> Perfect for important warnings

> A regular blockquote

> [!NOTE]\n> Important information

![](InvalidURL)

'# Header\nAbc


## Images

This is a paragraph!

> Quote

Paragraph

![title](https://url.com/image.jpg)

[[_TOC_]]

***

Thematic Break

***

Divider

---

END

***

## List

- Item 1
  - Sub Item 1
- Item 2

***

Lift($L$) can be determined by Lift Coefficient ($C_L$) like the following
equation.

$$
L = \frac{1}{2} \rho v^2 S C_L
test
$$

***

## Table

| First Header  | Second Header |
| ------------- | ------------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |


# The Cleanable Readme

This is a markdown file with some javascript code blocks in it.

```js
var foo = 1;
```

Each block is parsed separately, to avoid linting errors about variable
assignment. Notice that `var foo` occurs twice in this markdown file,
but only once in each individual snippet.

The following code block has a few issues:

- semicolons
- type-insensitive equality comparison
- double-quoted string

```javascript
var foo = 2;
console.log("foo is two");
```

This non-js code block should be ignored by the cleaner and the linter:

```sh
echo i am a shell command
```


Martian is a Markdown parser to convert any Markdown content to Notion API block or RichText objects. It
uses [unified](https://github.com/unifiedjs/unified) to create a Markdown AST, then converts the AST into Notion
objects.

Designed to make using the Notion SDK and API easier. Notion API version 1.0.

### Supported Markdown Elements

- All inline elements (italics, bold, strikethrough, inline code, hyperlinks, equations)
- Lists (ordered, unordered, checkboxes) - to any level of depth
- All headers (header levels >= 3 are treated as header level 3)
- Code blocks, with language highlighting support
- Block quotes
  - Supports GFM alerts (e.g. [!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION])
  - Supports Notion callouts when blockquote starts with an emoji (optional, enabled with `enableEmojiCallouts`)
- Tables

## Usage

### Basic usage:

The package exports two functions, which you can import like this:

```ts
// JS
const {markdownToBlocks, markdownToRichText} = require('@tryfabric/martian');
// TS
import {markdownToBlocks, markdownToRichText} from '@tryfabric/martian';
```

Here are couple of examples with both of them:

```ts
markdownToRichText(`**Hello _world_**`);
```

<details>
<summary>Result</summary>
<pre>
[
  {
    "type": "text",
    "annotations": {
      "bold": true,
      "strikethrough": false,
      "underline": false,
      "italic": false,
      "code": false,
      "color": "default"
    },
    "text": {
      "content": "Hello "
    }
  },
  {
    "type": "text",
    "annotations": {
      "bold": true,
      "strikethrough": false,
      "underline": false,
      "italic": true,
      "code": false,
      "color": "default"
    },
    "text": {
      "content": "world"
    }
  }
]
</pre>
</details>

```ts
markdownToBlocks(`
hello _world_ 
*** 
## heading2
* [x] todo

> 📘 **Note:** Important _information_

> Some other blockquote
`);
```


### Working with blockquotes

Martian supports three types of blockquotes:

1. Standard blockquotes:

```md
> This is a regular blockquote
> It can span multiple lines
```

2. GFM alerts (based on [GFM Alerts](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts)):

```md
> [!NOTE]
> Important information that users should know

> [!WARNING]
> Critical information that needs attention
```

3. Emoji-style callouts (optional) (based on [ReadMe's markdown callouts](https://docs.readme.com/rdmd/docs/callouts)):

```md
> 📘 **Note:** This is a callout with a blue background
> It supports all markdown formatting and can span multiple lines

> ❗ **Warning:** This is a callout with a red background
> Perfect for important warnings
```

#### GFM Alerts

GFM alerts are automatically converted to Notion callouts with appropriate icons and colors:

- NOTE (📘, blue): Useful information that users should know
- TIP (💡, green): Helpful advice for doing things better
- IMPORTANT (☝️, purple): Key information users need to know
- WARNING (⚠️, yellow): Urgent info that needs immediate attention
- CAUTION (❗, red): Advises about risks or negative outcomes

#### Emoji-style Callouts

By default, emoji-style callouts are disabled. You can enable them using the `enableEmojiCallouts` option:

```ts
const options = {
  enableEmojiCallouts: true,
};
```

When enabled, callouts are detected when a blockquote starts with an emoji. The emoji determines the callout's background color. The current supported color mappings are:

- 📘 (blue): Perfect for notes and information
- 👍 (green): Success messages and tips
- ❗ (red): Warnings and important notices
- 🚧 (yellow): Work in progress or caution notices

All other emojis will have a default background color. The supported emoji color mappings can be expanded easily if needed.

If a blockquote doesn't match either GFM alert syntax or emoji-style callout syntax (when enabled), it will be rendered as a Notion quote block.

##### Examples

Standard blockquote:

```ts
markdownToBlocks('> A regular blockquote');
```

<details>
<summary>Result</summary>
<pre>
[
  {
    "object": "block",
    "type": "quote",
    "quote": {
      "rich_text": [
        {
          "type": "text",
          "text": {
            "content": "A regular blockquote"
          }
        }
      ]
    }
  }
]
</pre>
</details>


Built with 💙 by the team behind [Fabric](https://tryfabric.com).

<img src="https://static.scarf.sh/a.png?x-pxid=79ae4e0a-7e48-4965-8a83-808c009aa47a" />
