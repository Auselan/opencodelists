console.log("builder3");
// TODO use querySelector
import htm from "htm";
import vhtml from "vhtml";

const html = htm.bind(vhtml);

import { readValueFromPage } from "./utils";
import Hierarchy from "./hierarchy";

const codeToTerm = readValueFromPage("code-to-term");
const codeToStatus = readValueFromPage("code-to-status");
const hierarchy = new Hierarchy(
  readValueFromPage("parent-map"),
  readValueFromPage("child-map")
);

const setup = () => {
  const ancestorNodes = document.getElementsByClassName("tree-ancestor");
  Array.from(ancestorNodes).forEach((node) => {
    const code = node.dataset["code"];
    const tree = buildTree(code, 2, null, null, null);
    node.innerHTML = renderTree(tree);
  });
};

const addChildren = (node) => {
  const childrenNode = node.querySelector(".tree-children");
  const code = node.dataset["code"];
  const childCodes = hierarchy.childMap[code];
  const pipes = Array.from(node.querySelectorAll(".tree-pipe")).map(
    (node) => node.innerHTML
  );
  const isLastSibling = pipes[pipes.length - 1] === "└";

  childCodes.forEach((childCode, ix) => {
    const childIsLastSibling = ix === childCodes.length - 1;
    const tree = buildTree(
      childCode,
      1,
      childIsLastSibling,
      isLastSibling,
      pipes
    );
    childrenNode.innerHTML += renderTree(tree);
  });
};

const buildTree = (
  code,
  depth,
  isLastSibling,
  parentIsLastSibling,
  parentPipes
) => {
  const childCodes = hierarchy.childMap[code] || [];

  // Sort childCodes by corresponding term
  childCodes.sort((code1, code2) => {
    const term1 = codeToTerm[code1];
    const term2 = codeToTerm[code2];
    if (term1 < term2) {
      return -1;
    } else if (term2 < term1) {
      return 1;
    } else {
      return 0;
    }
  });

  const newDepth = hierarchy.allDescendantsHaveSameStatus(code, codeToStatus)
    ? depth - 1
    : depth;

  // Pipes are used to show the relationship between nodes in the tree.  A node at depth
  // N has N pipes.  A node's pipes are determined by:
  //
  //  (a) the node's parent's pipes
  //  (b) whether the node's parent is the last of its siblings
  //  (c) whether the node itself is the last of its siblings
  //
  // Consider the following tree, with the array of pipes for each node in the RH column:
  //
  // A                  []
  // ├ B                ["├"]
  // │ ├ D              ["│", "├"]
  // │ │ ├ H            ["│", "│", "├"]
  // │ │ └ I            ["│", "│", "└"]
  // │ └ E              ["│", "└"]
  // │   ├ J            ["│", " ", "├"]
  // │   └ K            ["│", " ", "└"]
  // └ C                ["└"]
  //   ├ F              [" ", "├"]
  //   │ ├ L            [" ", "│", "├"]
  //   │ └ M            [" ", "│", "└"]
  //   └ G              [" ", "└"]
  //     ├ N            [" ", " ", "├"]
  //     └ O            [" ", " ", "└"]
  //
  //  There are three cases to consider:
  //
  //  (1) A node at depth 0 (ie the root)
  //      * It has no pipes
  //  (2) A node at depth 1 (ie a chlid of the root)
  //      * It has a single pipe, which is determined by whether it is the last of its
  //        siblings.
  //  (3) A node at depth N (with N > 1)
  //      * Its last pipe is determined by whether it is the last of its siblings
  //      * Its penultimate pipe is determined by whether its parent is the last of its
  //        siblings
  //      * The other pipes are all but the last of the parent's pipes
  let pipes;
  if (parentPipes === null) {
    // This is the root of the tree
    pipes = [];
  } else if (parentPipes.length === 0) {
    // This is a child of the root of the tree
    pipes = [isLastSibling ? "└" : "├"];
  } else {
    pipes = parentPipes
      .slice(0, -1)
      .concat(parentIsLastSibling ? " " : "│")
      .concat(isLastSibling ? "└" : "├");
  }

  const children =
    depth === 1
      ? []
      : childCodes.map((childCode, ix) =>
          buildTree(
            childCode,
            newDepth,
            ix === childCodes.length - 1,
            isLastSibling,
            pipes
          )
        );

  return {
    code: code,
    term: codeToTerm[code],
    status: codeToStatus[code],
    pipes: pipes,
    expandable: childCodes.length > 0,
    expanded: childCodes.length > 0 && children.length > 0,
    children: children,
  };
};

const renderTree = (tree) => {
  const { code, term, status, pipes, expandable, expanded, children } = tree;
  return html`<div
    class="tree-node mt-0"
    data-code=${code}
    data-expanded=${expanded}
  >
    <div class="tree-item d-flex">
      <div class="tree-buttons btn-group btn-group-sm" role="group">
        ${renderIncludeExcludeButton("+", status)}
        ${renderIncludeExcludeButton("-", status)}
      </div>

      <div class="tree-pipes pl-2 d-flex">
        ${pipes.map((pipe) => renderPipe(pipe))}
      </div>

      ${expandable && renderVisibilityToggle(expanded)}

      <div class="tree-term-and-code" style="white-space: nowrap;">
        <span>${term}</span>
        <span class="ml-1"> (<code>${code}</code>)</span>
      </div>
    </div>

    <div class="tree-children">
      ${children.map((child) => renderTree(child))}
    </div>
  </div>`;
};

const renderIncludeExcludeButton = (symbol, status) => {
  let buttonClass =
    status === symbol
      ? "btn-primary"
      : status === `(${symbol})`
      ? "btn-secondary"
      : "btn-outline-secondary";
  buttonClass = `btn ${buttonClass} py-0`;
  return html`<button type="button" class=${buttonClass}>${symbol}</button>`;
};

const renderVisibilityToggle = (expanded) => {
  return html`<div
    class="tree-visibility-toggle"
    style="cursor: pointer; margin-left: 2px; margin-right: 4px;"
  >
    ${expanded ? "⊟" : "⊞"}
  </div>`;
};

const renderPipe = (pipe) => {
  return html`<span
    class="tree-pipe"
    style="display: inline-block; text-align: center; padding-left: 3px; padding-right: 6px; width: 20px;"
  >
    ${pipe}
  </span>`;
};

const toggleVisibility = (visibilityToggle) => {
  const node = visibilityToggle.closest(".tree-node");
  const childrenNode = node.querySelector(".tree-children");

  if (node.hasAttribute("data-expanded")) {
    // node is expanded, so collapse it
    childrenNode.setAttribute("hidden", "");
    node.removeAttribute("data-expanded");
    visibilityToggle.innerHTML = "⊞";
  } else {
    // node is collapsed, so expand it
    if (childrenNode.childElementCount === 0) {
      // node's children haven't been added yet, so add them
      addChildren(node);
    }
    childrenNode.removeAttribute("hidden");
    node.setAttribute("data-expanded", "");
    visibilityToggle.innerHTML = "⊟";
  }
};

document.addEventListener("DOMContentLoaded", setup);

document.addEventListener("click", (event) => {
  event.preventDefault();
  event.target.matches(".tree-visibility-toggle") &&
    toggleVisibility(event.target);
});
