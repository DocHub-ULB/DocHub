const React = require('react');
const ReactDOM = require('react-dom');
const MetisMenu = require('react-metismenu').default;

/*
 * The 2 functions below take a node returned from the API as argument and
 * return a JS object suitable for MetisMenu. Here, we also need the parent
 * in the hierarchy, because the same course can belong to different categories.
 * Therefore, to correctly display an opened menu with the same path as the
 * user took to get there, we need to reference the parent, and append it in
 * the URL hash.
 * 
 * See also https://github.com/alpertuna/react-metismenu/#active-link-selectors
 */

const courseToMenu = parent =>
    course => {
        return {
            icon: 'book',
            label: course.name,
            to: `/catalog/course/${course.slug}#_${parent}`
        };
    };

const categoryToMenu = parent =>
    category => {
        let subcategories = category.children.map(categoryToMenu(category.id));
        let courses = category.courses.map(courseToMenu(category.id));
        return {
            icon: 'folder',
            label: category.name,
            to: `/catalog/category/${category.id}#_${parent}`,
            content: subcategories.concat(courses)
        };
    };

const SideTree = ({content}) =>
    <MetisMenu content={content.map(categoryToMenu(""))}
               iconNamePrefix='fi-'
               activeLinkFromLocation />;

module.exports = SideTree;
